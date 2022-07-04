

.PHONY: publish

tox_py_git_source="https://github.com/sanekits/tox.git"
tox_files=bin/tox_core.py bin/setutils.py bin/tox-completion.bash

publish: $(tox_files)
	publish/publish-via-github-release.sh
