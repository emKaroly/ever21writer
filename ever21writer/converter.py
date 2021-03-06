import json
import os
import sys
from csv import DictWriter
from cStringIO import StringIO
from dateutil.parser import parse
from html2text import HTML2Text
from lxml import etree

class EverConverter(object):
    """Evernote conversion runner
    """

    fieldnames = ['createdate', 'modifydate', 'content', 'tags','gps']
    date_fmt = '%h %d %Y %H:%M:%S'

    def __init__(self, enex_filename, simple_filename=None, fmt='json'):
        self.enex_filename = os.path.expanduser(enex_filename)
        self.stdout = False
        if simple_filename is None:
            self.stdout = True
            self.simple_filename = simple_filename
        else:
            self.simple_filename = os.path.expanduser(simple_filename)
        self.fmt = fmt

    def _load_xml(self, enex_file):
        try:
            parser = etree.XMLParser(huge_tree=True)
            xml_tree = etree.parse(enex_file, parser)
        except (etree.XMLSyntaxError, ), e:
            print 'Could not parse XML'
            print e
            sys.exit(1)
        return xml_tree

    def prepare_notes(self, xml_tree):
        map_notes = {}
        raw_notes = xml_tree.xpath('//note')
        for note in raw_notes:
            note_dict = {}
            title = note.xpath('title')[0].text
            note_dict['title'] = title
            # Use dateutil to figure out these dates
            # 20110610T182917Z
            created_string_raw = '19700101T000017Z'
            created_string = parse(created_string_raw)
            if note.xpath('created'):
                created_string = parse(note.xpath('created')[0].text)
                created_string_raw = note.xpath('created')[0].text
            updated_string = created_string
            if note.xpath('updated'):
                updated_string = parse(note.xpath('updated')[0].text)
            note_dict['createdate'] = created_string.strftime(self.date_fmt)
            note_dict['created_string_raw'] = created_string_raw
            note_dict['modifydate'] = updated_string.strftime(self.date_fmt)
            tags = [tag.text for tag in note.xpath('tag')]
            if self.fmt == 'csv':
                tags = " ".join(tags)
            note_dict['tags'] = tags
            raw_note_attributes = note.xpath('note-attributes')
            source_url = ''
            gps = "None"
            for note_attribute in raw_note_attributes:
                if note_attribute.xpath('source-url'):
                    source_url = note_attribute.xpath('source-url')[0].text
                if note_attribute.xpath('longitude'):
                    gps = "Lon:"
                    gps+=str(note_attribute.xpath('longitude')[0].text)
                if note_attribute.xpath('latitude'):
                    gps+= " Lat:"
                    gps+=str(note_attribute.xpath('latitude')[0].text)
                if note_attribute.xpath('altitude'):
                    gps+= " Alt:"
                    gps+=str(note_attribute.xpath('altitude')[0].text)
            note_dict['content'] = ''
            content = note.xpath('content')
            if content:
                raw_text = content[0].text
                converted_text = self._convert_html_markdown(title, raw_text, tags, gps, source_url, note_dict['created_string_raw'] )
                if self.fmt == 'csv':
                    # XXX: DictWriter can't handle unicode. Just
                    #      ignoring the problem for now.
                    converted_text = converted_text.encode('ascii', 'ignore')
                note_dict['content'] = converted_text
            map_notes.setdefault(created_string_raw,[]).append(note_dict)
        return map_notes

    def convert(self):
        if not os.path.exists(self.enex_filename):
            print "File does not exist: %s" % self.enex_filename
            sys.exit(1)
        # TODO: use with here, but pyflakes barfs on it
        enex_file = open(self.enex_filename)
        xml_tree = self._load_xml(enex_file)
        enex_file.close()
        notes = self.prepare_notes(xml_tree)
        if self.fmt == 'csv':
            self._convert_csv(notes)
        if self.fmt == 'json':
            self._convert_json(notes)
        if self.fmt == 'dir':
            self._convert_dir(notes)
        if self.fmt == '1writer':
            self._convert_dir(notes)

    def _convert_html_markdown(self, title, text, tags, gps, source_url, created_string_raw ):
        html2plain = HTML2Text(None, "")
        html2plain.feed("<h1>%s</h1>" % title)
        if self.fmt == '1writer':
            header_created = 0 
            if tags:
                header_created += 1
                html2plain.feed("<p>Tags: ")
                for i in (tags):
                    html2plain.feed("#%s " % i)
                html2plain.feed("</p>")
            if gps:
                header_created += 1
                html2plain.feed("<p>GPS: %s</p>" % gps)
            if source_url:
                html2plain.feed("<p><a href=\"%s\">Source</a></p>" % source_url )
                header_created += 1
            if created_string_raw:
                header_created += 1
                html2plain.feed("<p>Created: %s</p>" % created_string_raw)
            if header_created:
                html2plain.feed("<hr />")
        html2plain.feed(text)
        return html2plain.close()

    def _convert_csv(self, notes):
        if self.stdout:
            simple_file = StringIO()
        else:
            simple_file = open(self.simple_filename, 'w')
        writer = DictWriter(simple_file, self.fieldnames)
        writer.writerows(notes)
        if self.stdout:
            simple_file.seek(0)
            # XXX: this is only for the StringIO right now
            sys.stdout.write(simple_file.getvalue())
        simple_file.close()

    def _convert_json(self, notes):
        if self.simple_filename is None:
            sys.stdout.write(json.dumps(notes))
        else:
            with open(self.simple_filename, 'w') as output_file:
                json.dump(notes, output_file)

    def _convert_dir(self, map_notes):
        if os.path.exists(self.simple_filename) and not os.path.isdir(self.simple_filename):
            print '"%s" exists but is not a directory. %s' % self.simple_filename
            sys.exit(1)
        elif not os.path.exists(self.simple_filename):
            os.makedirs(self.simple_filename)
        k = map_notes.keys()
        k.sort()
        i = 0
        for created_string_raw in k:
            for note in map_notes[created_string_raw]:
                i += 1
                output_file_path = os.path.join(self.simple_filename, str(i).zfill(4) + '_' + note['created_string_raw'] + '.md')
                if os.path.exists(output_file_path):
                    print '"%s" file already exists, exiting' % output_file_path
                    sys.exit(1)
                else:
                    with open(output_file_path, 'w') as output_file:
                        output_file.write(note['content'].encode(encoding='utf-8'))

