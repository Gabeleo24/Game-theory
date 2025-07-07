# Jupyter Configuration for Researcher Role
# ADS599 Capstone Soccer Intelligence System

c = get_config()

# Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8890
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.notebook_dir = '/app/notebooks/research'

# Security configuration
c.ServerApp.token = 'researcher_secure_token_2024'
c.ServerApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$soccer_intelligence_research'
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = False

# Resource limits
c.ResourceUseDisplay.mem_limit = 6 * 1024**3  # 6GB
c.ResourceUseDisplay.track_cpu_percent = True

# File access restrictions
c.ContentsManager.allow_hidden = False
c.FileContentsManager.delete_to_trash = True

# Kernel management
c.MappingKernelManager.cull_idle_timeout = 1800  # 30 minutes
c.MappingKernelManager.cull_interval = 300       # 5 minutes

# Extensions
c.ServerApp.jpserver_extensions = {
    'jupyterlab': True,
    'jupyterlab_git': True,
    'jupyterlab_plotly': True,
    'jupyterlab_latex': True
}
