from ebooklib import epub
import ebooklib
import request
import tika
import os
from tika import parser


tika.initVM()

# harvest fragment
def harvest_from_url(url)
    r = requests.get(url, stream = True)
    size = r.headers['content-length']
    file_name = url.split('/')[-1]
    if len(file_name.split('.')) == 1: # file has no extension: append it
                file_name += '.'+extension
#    save content, return filename


def text_from_epub(fn): #obtain text content
    book = epub.read_epub(fn) # ebooklib.epub.EpubBook
#    for doc in book.get_items():
#   docs = [(doc,type(doc), doc.get_type) for doc in book.get_items()]
    i = 0
    content = ''
    for doc in book.get_items_of_type(9): # 9: EpubHtml, 4: EpubItem, 2: EpubItem, 1: EpubImage
        content += str(doc.content)
        i+=1
    assert i==1
    #NB html content - clean for special characters?
    return content

def text_from_pdf(fn):
    # do tika dance
    parsed = parser.from_file(fn)
    if 'content' in parsed:
        return parsed['content']
    else: 
        print('\tProblem with Tika (corrupt file?)')
        return None
    

def write_content(content, fn):
    with open(fn,'w') as f:
        f.write(content)


# url =
# fn = harvest_from_url(url)
for fn in [os.path.join('data'),n) for n in ['9789023910343_fragm.epub','9789044534801_fragm.pdf']]:
    r = fn.split('.')[0]
    ext = fn.split('.')[-1]
    if ext =='epub':
        content = text_from_epub(fn)
        pf = '_parsed.html'
    elif ext =='pdf':
        content = text_from_pdf(fn)
        pf = '_parsed.txt'
    else:
        print('Unknown ext:', ext)
    write_content(content, r+pf)








