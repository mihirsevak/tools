MY TOOLS

These are my tools to make my life easy.

marks and scripts are my tools I would require to do my job efficiently on any linux machine.

Password Generator generates and keep track of my passwords.

To set up Dev Environment on Windows install following tools
1) TDM-GCC (This includes gdb. YOu may require to install VC_redist.x64 and VC_redist.x86)
2) vim (To install auto-pair plugin for vim follow steps listed in section below)
4) clink (Command is: winget install -e --id christan996.Clink --source winget)
5) git bash
6) to start vim/gvim from command line first create a HOME variable in your USER Environment variable section. This variable should point to C:\Users\<username>. After that add path to your gvim/vim installation in System Variable PATH. If this order is not followed you will see defaults.vim file not found error.
7) to get all linux commands on windows point to git bash's bin directory in System variable PATH



To install plugins on VIM
--------------------------
Step 1: Create the plugin folderOpen your Windows File Explorer.Go to your user folder: C:\Users\YourUsername.Create this exact new folder path: vimfiles\pack\plugins\start.
Step 2: Download the pluginOpen your web browser and go to the auto-pairs GitHub Repository.Click the green Code button and download the ZIP file.Open the ZIP file.Copy the plugin folder inside the ZIP.Paste it into your start folder (located at C:\Users\YourUsername\vimfiles\pack\plugins\start).
Step 3: Turn on VimOpen Vim from your command prompt or terminal. The plugin loads automatically every time you open a file.How to use itType an opening bracket ( or quote ". The plugin will close it (|) automatically.Press BackSpace to delete both pairs at the same time.
