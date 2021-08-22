

.PHONY: publish tox_borrow tox_py_update

tox_py_git_source="https://github.com/sanekits/tox.git"
tox_files=bin/tox_core.py bin/setutils.py bin/tox-completion.bash

publish: tox_borrow
	publish/publish-via-github-release.sh

tox_borrow: tox_py_update $(tox_files)
	# Copying tox-py essentials to bin for packaging
	-command git add $(tox_files) && command git commit -m "Update tox_files"

tox_py_update: tox-py
	cd tox-py && git pull

tox-py:
	git clone $(tox_py_git_source) tox-py

bin/%: tox-py/%  # Update bin/ from tox-py/
	cp $< bin/
