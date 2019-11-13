## Installation

This is the client CLI for ACAI System.

Notice that **Python3** is required. 
[ACAI SDK](https://acai-systems.github.io/acaisdk/)
will be installed as a dependency.

```bash
git clone https://github.com/acai-systems/acaicli.git
cd acaicli/
pip3 install .

# If not sure which Python executable pip3 is linked with, 
# alternatively, you can do 
python3 -m pip install .

# Log in to the system by exporting ENV variables
export ACAI_TOKEN=****************

# Show help
acai -h
```

Some examples:
```bash
# List all files (add "-l" to show more info) 
acai ls

# List all file sets
acai ls @

# List files in specific file set
acai ls @my_file_set
```
