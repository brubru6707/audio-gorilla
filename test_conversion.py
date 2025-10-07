import re

def f(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

print('GoogleDrive:', repr(f('GoogleDrive')))
print('YouTube:', repr(f('YouTube')))
print('X:', repr(f('X')))
print('Gmail:', repr(f('Gmail')))
print('Amazon:', repr(f('Amazon')))