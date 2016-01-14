test:prepare
	venv/bin/pip install mock==0.8.0
	venv/bin/python setup.py test

clean:
	rm -rf venv build dist *.egg-info python-*
	rm -f *.tar.gz
	find . -name '*.pyc ' -delete

prepare:clean
	set -ex
	virtualenv venv
	git clone -b staging https://github.com/tutumcloud/python-dockercloud.git && cd python-dockercloud && ../venv/bin/python setup.py install && cd .. && rm -rf python-dockercloud
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install .
retest:
	venv/bin/python setup.py test

certs:
	curl http://ci.kennethreitz.org/job/ca-bundle/lastSuccessfulBuild/artifact/cacerts.pem -o cacert.pem

build-osx:prepare
	if [ ! -f cacert.pem ]; then make certs; fi
	venv/bin/pip install pyinstaller
	venv/bin/pyinstaller tutum.spec -y
	mv dist/tutum tutum
	tutum/tutum -v
	tar zcvf tutum-Darwin-x86_64.tar.gz tutum
	rm -rf tutum
	mv tutum-Darwin-x86_64.tar.gz dist/tutum-Darwin-x86_64.tar.gz

publish-osx:build-osx
	venv/bin/pip install awscli
	venv/bin/aws s3 cp dist/tutum-Darwin-x86_64.tar.gz s3://files.tutum.co/packages/tutum-cli/Darwin/x86_64/tutum-`cat tutumcli/__init__.py |grep version | grep -o "\'.*\'" | sed "s/'//g"`.tar.gz --acl public-read

publish-pypi:prepare
	python setup.py sdist upload
