import os  
lst=os.listdir(os.getcwd())   
 
for c in lst:
  if os.path.isfile(c) and c.endswith('.py') and c.find("run-all")==-1:
    os.system("python ./%s" % c) 