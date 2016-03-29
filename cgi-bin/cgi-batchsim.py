#!/home/sajadi/anaconda2/bin/python
#/users/grad/sajadi/anaconda2/bin/python

import cgi, os
import cgitb; cgitb.enable()
import tempfile
import time
import sys

from calcsim import *
from shutil import copyfile
import json


log('cgi-batchsim started');
print "Content-type:application/json\r\n\r\n"

tmpdir = os.path.join(outdir, 'tmp')
if not os.path.exists(tmpdir):
    os.makedirs(tmpdir)
    os.chmod(tmpdir, 0777)    
    log('tmp directory generated');

resultfile = os.path.join(outdir, 'results.html')
if not os.path.exists(resultfile):
    copyfile(os.path.join(outdir, 'results.orig.html'),resultfile)
    os.chmod(resultfile, 0777)    


form = cgi.FieldStorage()


# Get filename here.

fileitem = form['file']

#Test if the file was uploaded
if fileitem.filename:
    # strip leading path from file name to avoid 
    # directory traversal attacks
    fn = os.path.basename(fileitem.filename)
    fnbase, fnext = os.path.splitext(fn);
    # sudo chown www-data tmp
    timestr = time.strftime("%Y%m%d-%H%M%S")

    infn=os.path.join(tmpdir, timestr+'-'+fn)
    outfn_rel= os.path.join('tmp', timestr+'-'+fnbase+'.out'+fnext)
    outfn=      os.path.join(outdir, outfn_rel)

    with open(infn, 'wb') as f:
        f.write(fileitem.file.read())   
else:
    print json.dumps({"redirect":"../error.html"})
    exit()


# Update result file
import datetime
from bs4 import BeautifulSoup as soup

with open(resultfile,'r') as f:
    html=f.read()
sp = soup(html,'lxml')
resdiv= sp.find("div", {"id": "resultsdiv"})
newhtml="""
            <div class="alert alert-warning " role="alert">
                <p>
                	<b>Job Id {0}</b>: Processing {1} started at: {2}, save this Job Id and refresh this page 
                	until the results are posted
                </p>
            </div>            
        """.format(timestr, infn, datetime.datetime.now());
new_tag = soup(newhtml, 'lxml')
new_tag=new_tag.body.next
resdiv.append(new_tag)
with open(resultfile,'w') as f:
    f.write(sp.prettify())

# Starting the process



task=form.getvalue('task')

direction =int(form.getvalue('dir'))
log('cutoff%s', 'cutoff');

cutoff=form.getvalue('cutoff')
cutoff = None if cutoff.lower()=="all" else int(cutoff)

log('cutoff%s', cutoff);


if task == 'sim':
    getsim_file(infn, outfn, 'rvspagerank', direction);
elif task == 'emb':
    getembed_file(infn, outfn, direction, cutoff=cutoff);



# Update result file

with open(resultfile,'r') as f:
    html=f.read()

sp = soup(html)
resdiv= sp.find("div", {"id": "resultsdiv"})
newhtml="""
            <div class="alert alert-success " role="alert">
                <p>
                	JobId: {0}: Done at {1}, download the results from:  
                </p>
                <a href={2}>{3}
                </a>
           </div>            
        """.format(timestr, datetime.datetime.now(), outfn_rel, outfn_rel);
new_tag = soup(newhtml)
new_tag=new_tag.body.next

resdiv.append(new_tag)
with open(resultfile,'w') as f:
    f.write(sp.prettify())

import json
print json.dumps({"redirect":"out/results.html"})


