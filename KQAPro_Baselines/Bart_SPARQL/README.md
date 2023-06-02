## Requirements
- python3.7
- rdflib=4.2.2 or 6.1.1
- transformers
---
**Note for rdflib 4.2.2:** 
After installing rdflib via `pip` or `anaconda` or some other tools, we need to fix some bugs of it.

First, find your rdflib location. One possible way is to run following codes in ipython 
```
import rdflib
rdflib.__file__
```
It returns `~/anaconda3/lib/python3.7/site-packages/rdflib/__init__.py` in my computer, so I enter the folder `~/anaconda3/lib/python3.7/site-packages/rdflib`.

Then open `plugins/sparql/parser.py`, find *Line 68*, replace its code with
```
if i + 1 < l and (not isinstance(terms[i + 1], str) or terms[i + 1] not in ".,;"):
```
Remember to keep the original indentation.
Note that *Line 67* is a comment of `# is this bnode the subject of more triplets?`. If your line number is different from mine, you could locate the target line by this comment.

Finally, open `plugins/serializers/turtle.py`, find *Line 328*, change `use_plain=True` to `use_plain=False`


**Note for rdflib 6.1.1:** 
If you have an erro " can't set attribute" with rdflib=4.2.2,you should try rdflib=6.1.1 .

---

- SPARQLWrapper=1.8.4

---
**Note:** 
When installing `SPARQLWrapper` with `pip`, it may automatically install another package `keepalive`. You can check whether it is in your environment by
```
pip show keepalive
```

If it is installed, it will cause some problems when we execute a large number of SPARQL queries. Specifically, the available ports will be used out. So we need to manually disable the `keepalive` package. It is okay to directly remove it.
```
pip uninstall keepalive
```

---

- Virtuoso backend, refer to the next section

## How to install virtuoso backend
The virtuoso backend will start up a web service, we can import our kb into it and then execute SPARQL queries by network requests. We install virtuoso in an Ubuntu 16.04 system. Following are specific steps.

1. Download and install virtuoso into our system.
```
git clone https://github.com/openlink/virtuoso-opensource.git Virtuoso-Opensource
cd Virtuoso-Opensource
git checkout stable/7
sudo apt-get install libtool gawk gperf autoconf automake libtool flex bison m4 make openssl libssl-dev
sudo ./autogen.sh
sudo ./configure
sudo make
sudo make install
```

2. Create a new user for virtuoso service
```
sudo useradd virtuoso --home /usr/local/virtuoso-opensource
sudo chown -R virtuoso /usr/local/virtuoso-opensource
```

3. Modify some necessary configs:
```
cd /usr/local/virtuoso-opensource/var/lib/virtuoso/db
sudo vim virtuoso.ini
```
Find the item `CheckpointInterval`, and change its value from default 60 to 0, to avoid automatical checkpoint process which will cause 404 error.

4. Start up the virtuoso service:
```
sudo -H -u virtuoso ../../../../bin/virtuoso-t -f &
```
Now you can access the service via the default port 8890.
Enter `[ip]:8890` in a browser, you will see the virtuoso service page.

[note] The virtuoso may report an erro "There is no configuration file virtuoso.ini" when start up. 
```
sudo vim /etc/rc.conf
```
Add a line：`virtuoso_config="/usr/local/virtuoso-opensource/var/lib/virtuoso/db/virtuoso.ini"`


5. Now we can import our kb into virtuoso. Before that, we need to convert our kb to `ttl` format and move it to proper position:
```
python -m Bart_SPARQL.sparql_engine --kb_path dataset/kb.json --ttl_path dataset/kb.ttl
sudo chmod 777 dataset/kb.ttl
sudo mv dataset/kb.ttl /usr/local/virtuoso-opensource/share/virtuoso/vad
```

6. Enter the interactive terminal of virtuoso:
```
cd /usr/local/virtuoso-opensource/bin
sudo ./isql
```

7. Import our kb by executing these commands in terminal:
```
SPARQL CREATE GRAPH <[graph_name]>;
SPARQL CLEAR GRAPH <[graph_name]>;
delete from db.dba.load_list;
ld_dir('/usr/local/virtuoso-opensource/share/virtuoso/vad', 'kb.ttl', '[graph_name]');
rdf_loader_run();
select * from DB.DBA.load_list;
exit;
```
`[graph_name]` could be any legal string, such as *KQAPro*.
You are success if `rdf_loader_run()` lasts for about 10 seconds.


## How to run
1. Follow the last section, start up the virtuoso service and import `kb.ttl`. Then you need to open `sparql_engine.py` and find the lines of
```
virtuoso_address = "http://127.0.0.1:8890/sparql"
virtuoso_graph_uri = 'sjx'
```
Change `virtuoso_address` to your service url (you can visit it in your browser to check whether it is valid) and change `virtuoso_graph_uri` to your `<graph_name>`.
2. Preprocess the training data
```
python -m Bart_SPARQL.preprocess --input_dir ./dataset --output_dir <dir/of/processed/files> --model_name_or_path <dir/of/pretrained/BartModel>
cp ./dataset/kb.json <dir/of/processed/files>
```
3. Train
```
python -m Bart_SPARQL.train --input_dir <dir/of/processed/files> --output_dir <dir/of/checkpoint> --model_name_or_path <dir/of/pretrained/BartModel> --save_dir <dir/of/log/files>
```
4. Predict answers of the test set. It will produce a file named `predict.txt` in the `--save_dir`, storing the predictions of test questions in order.
```
python -m Bart_SPARQL.predict --input_dir <dir/of/processed/files> --ckpt <dir/of/checkpoint> --save_dir <dir/of/log/files>

```

## Checkpoints
1. The pretrained Bart-base checkpoint without finetuning can be downloaded here [bart-base](https://cloud.tsinghua.edu.cn/f/3b59ec6c43034cfc8841/?dl=1)
2. The checkpoint for finetuned Bart_SPARQL can be downloaded here [finetuned](https://cloud.tsinghua.edu.cn/f/1b9746dcd96b4fca870d/?dl=1)
