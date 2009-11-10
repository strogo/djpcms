
import quickutils

def install(PS, djpcms = False):
    putils  = quickutils.PackageInstaller(__file__)
    addname = True
    if not PS.dev:
        addname = False
    
    PS.LOCDIR        = putils.dir
    
    if djpcms:
        PS.djpcms_path   = putils.install('djpcms', up = 1, addname = addname)
        if PS.servs:
            PS.MEDIA_ROOT  = putils.directory(PS.LOCDIR, 'media')
        else:
            PS.MEDIA_ROOT  = PS.media_root
            
    PS.txdjango_path = putils.install('txdjango', up = 1, addname = addname)
    PS.jflow_path    = putils.install('jflow', up = 1, addname = addname)
    PS.ccy_path      = putils.install('ccy', up = 1, addname = addname)
    PS.flowrepo_path = putils.install('flowrepo', up = 1, addname = addname)
    PS.amazon        = putils.install('amazon', up = 1, addname = addname)
    PS.mineflow      = putils.install('mineflow', up = 1, addname = addname)
    
    PS.plugins_ext   = putils.adddir(PS.jflow_path, 'plugins', 'externals')
    PS.plugins_int   = putils.adddir(PS.jflow_path, 'plugins', 'internals')
    
    PS.txdjango_ext  = putils.adddir(PS.txdjango_path, 'libs', 'externals')
    PS.txdjango_int  = putils.adddir(PS.txdjango_path, 'libs', 'internals')
    
    PS.local_apps    = putils.adddir(PS.LOCDIR, 'apps')
    PS.local_plugins = putils.adddir(PS.LOCDIR, 'plugins')
    
    
