from ebooklib import epub
import ebooklib
import requests
import tika
import os
from bs4 import BeautifulSoup
from tika import parser
import glob
from lxml import etree





# harvest fragment
def harvest_from_url(url, output_file):
    r = requests.get(url, stream = True)
    content_type, extension = r.headers['content-type'].split(';')[0].split('/')
    size = r.headers['content-length']
    with open(output_file+'.'+extension, 'wb') as fh:
        shutil.copyfileobj(r.raw, fh)
    return extension

#    save content, return filename


def text_from_epub(fn): #obtain text content
    book = epub.read_epub(fn) # ebooklib.epub.EpubBook
#    for doc in book.get_items():
#   docs = [(doc,type(doc), doc.get_type) for doc in book.get_items()]
    i = 0
    for doc in book.get_items_of_type(9): # 9: EpubHtml, 4: EpubItem, 2: EpubItem, 1: EpubImage
        content = doc.content
        i+=1
    assert i==1
    soup = BeautifulSoup(content, features="lxml")
    content=soup.get_text('\n',strip=False)
    #NB html content - clean for special characters?
    return content

def text_from_pdf(fn):
    # do tika dance
    parsed = parser.from_file(fn)
    if 'content' in parsed and parsed['content'] is not None:
        return parsed['content']
    else:
        print('\tProblem with Tika (corrupt file? Empty content?)',fn)
        return None


def write_content(content, fn):
    with open(fn,'w') as f:
        f.write(content)




def fetch_fragment(url, identifier):
    ext = harvest_from_url(url, output_file = identifier)
    if ext =='epub':
        content = text_from_epub(fn)
    elif ext =='pdf':
        content = text_from_pdf(fn)
    else:
        print('Unknown ext:', ext)
    write_content(content, identifier+'_parsed.txt')

resource_cts = {'front_cover': '01', 'back_cover': '02', 'sample_content': '15', 'full_content':'28'}

def process_onix(fn='data/ONIX30MEAS20160330-INI-1van3.onx', download_fragments=True):
    xml = etree.parse(fn)
    root = xml.getroot()
    ns = root.nsmap
    for product in root.findall('Product', namespaces=ns):
        isbn=product.find('RecordReference', namespaces=ns).text
        print(isbn)
        resources = product.findall("./CollateralDetail/SupportingResource", namespaces=ns)
        if download_fragments:
            fragments = [r for r in resources if r.find('ResourceContentType',namespaces=ns).text == resource_cts['sample_content']]
            fragment_urls = [r.find("ResourceVersion/ResourceLink" , namespaces=ns).text for r in fragments]

            if len(glob.glob(isbn+'_fragm_')) < len(fragment_urls):  # not already downloaded
                for i, url in enumerate(fragment_urls):
                    print('\t Fetch', url)
                    fetch_fragment(url, isbn+'_fragm_'+str(i))




def main():
    tika.initVM()
    onix_file = 'data/ONIX30MEAS20160330-INI-1van3_minisample.onx'
    process_onix(onix_file)
    


    # url =
# fn = harvest_from_url(url)
#     for fn in [os.path.join('data',n) for n in ['9789023910343_fragm.epub','9789044534801_fragm.pdf']]:
#         r = fn.split('.')[0]
#         ext = fn.split('.')[-1]
#         if ext =='epub':
#             content = text_from_epub(fn)
#         elif ext =='pdf':
#             content = text_from_pdf(fn)
#         else:
#             print('Unknown ext:', ext)
#         write_content(content, r+'_parsed.txt')


# ugly way to sample from onix:
# xml = etree.parse('ONIX30MEAS20160330-INI-1van3.onx')
# r = xml.getroot()
# # len(r) is 2452, prune to 500:
# for product in random.sample(population=r[1:], k=1951): r.remove(product)
# xml.write(file='ONIX30MEAS20160330-INI-1van3_sample.onx')

main()
