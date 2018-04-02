from Redy.Types import *


from Redy.Tools import Path
p = Path('.')
p.abs()
p.is_dir()
p.list_dir()
p.parent()
list(p.collect())
p.__iter__()
new = p.into('justfortest')
new.mkdir()
new.mkdir()
new.delete()
p.relative()
new.open('w')
new.delete()