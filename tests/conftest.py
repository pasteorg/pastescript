import sys
import os
import shutil

here = os.path.dirname(__file__)
base = os.path.dirname(here)
fake_packages = os.path.join(here, 'fake_packages')
sys.path.append(fake_packages)
sys.path.insert(0, base)

# We can only import this after we adjust the paths
import pkg_resources

egg_info_dir = os.path.join(here, 'fake_packages', 'FakePlugin.egg',
                            'EGG-INFO')
info_dir = os.path.join(here, 'fake_packages', 'FakePlugin.egg',
                        'FakePlugin.egg-info')

if not os.path.exists(egg_info_dir):
    try:
        os.symlink(info_dir, egg_info_dir)
    except:
        shutil.copytree(info_dir, egg_info_dir)
        
pkg_resources.require('FakePlugin')
