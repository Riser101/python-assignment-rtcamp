#!/usr/bin/env python3
import subprocess as sp
import os
import pymysql
import socket
import urllib.request
import tarfile
import os
import errno
from cement.core import foundation

# create the application
app = foundation.CementApp('rtcamp-assign')

# then setup the application... which will use our 'mylog' handler
app.setup()

# add any arguments after setup(), and before run()
app.args.add_argument('-php', action='store_true', dest='php',
                      help='checks or installs php')
app.args.add_argument('-mysql', action='store_true', dest='mysql',
                      help='checks or installs mysql')
app.args.add_argument('-nginx', action='store_true', dest='nginx',
                      help='checks or installs nginx and sets up wordpress')

# then run the application
app.run()

# access the parsed args from the app.pargs shortcut
if app.pargs.php:
  def hasPHP():
   try:
    print("\n")
    sp.check_call(['php','--version'])
    return True
   except:
    os.system('sudo apt-get update')
    os.system('sudo apt-get install php5-fpm')
    os.system('sudo apt-get install php5-mysql')
    os.system('sudo apt-get install php5-cli')
    return False
  hasPHP()

if app.pargs.mysql:
 def hasMYSQL():
  try:
   print("\n")
   sp.check_call(['mysql','--version'])
   return True
  except:
   os.system('sudo apt-get install mysql-server')
   os.system('sudo apt-get install mysql-client')
   return False

 hasMYSQL()

if app.pargs.nginx:
 def hasNGINX():
  try:
   sp.check_call('nginx','-v')
   return True
  except:
   os.system('sudo apt-get install nginx')
   return False
 
 hasNGINX()
 domainName=input("\nEnter a domain name of your choice:")

 s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 s.connect(("8.8.8.8",80))
 myip=s.getsockname()[0]
 s.close()

 f= open('/etc/hosts','a')
 f.write("\n"+myip+" "+domainName+" "+"www."+domainName)
 f.close()

 open('/etc/nginx/sites-available/'+domainName,'a').close()
 a=open('/etc/nginx/sites-available/'+domainName,'a')
 a.write("server {"
        "\n\tserver_name"+" "+domainName+" "+"www."+domainName+";"

	"\n\n\taccess_log   /var/log/nginx/"+domainName+".access.log;"
	"\n\terror_log    /var/log/nginx/"+domainName+".error.log;"

        "\n\n\troot /var/www/"+domainName+"/htdocs;"
        "\n\tindex index.php;"

        "\n\n\tlocation / {"
                "\n\t\ttry_files $uri $uri/ /index.php?$args;"
        "\n\t}"

        "\n\n\tlocation ~ \.php$ {"
                "\n\t\ttry_files $uri =404;"
                "\n\t\tinclude fastcgi_params;"
                "\n\t\tfastcgi_pass unix:/var/run/php5-fpm.sock;"
                "\n\t\tfastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;" 
                
        "\n\n\t}"
 "\n\n}")
 a.close()

 os.symlink('/etc/nginx/sites-available/'+domainName+'','/etc/nginx/sites-enabled/'+domainName+'')
 try:
  os.makedirs('/var/www/'+domainName+'/htdocs/')
 except OSError as exc: 
    if exc.errno == errno.EEXIST and os.path.isdir(path):
     pass
 try:
  os.makedirs('/var/www/'+domainName+'/logs/')
 except OSError as exc: 
    if exc.errno == errno.EEXIST and os.path.isdir(path):
     pass
 path='/var/www/'+domainName+'/htdocs/'
 os.chdir(path)	 
 print("Downloading Wordpress, please wait......")
 url='http://wordpress.org/latest.tar.gz'
 f = urllib.request.urlopen(url)
 data = f.read()
 with open("/var/www/"+domainName+"/htdocs/latest.tar.gz", "wb") as code:
  code.write(data)
 tar = tarfile.open("/var/www/"+domainName+"/htdocs/latest.tar.gz","r:gz")
 tar.extractall("/var/www/"+domainName+"/htdocs/") 
 os.system('chown -R www-data:www-data /var/www/'+domainName+'/ ')
 rootpass=input('Please type in your root password of mysql:')
 
 try:
  conn=pymysql.connect(user='root',passwd=''+rootpass)
  conn.autocommit(True)
  cur=conn.cursor()
  cur.execute('CREATE DATABASE'+' '+"`"+domainName+'_db'+"`;")
  conn.close() 
 except:
  print("\n\n ooooops! Cannot connect to the database!")

 os.symlink('/var/log/nginx/'+domainName+'.access.log','/var/www/'+domainName+'/logs/access.log')
 os.symlink('/var/log/nginx/'+domainName+'.error.log','/var/www/'+domainName+'/logs/error.log')

 os.system('cp /var/www/'+domainName+'/htdocs/wp-config-sample.php /var/www/'+domainName+'/htdocs/wp-config.php')
#writing to wpconfig
 filename="/var/www/"+domainName+"/htdocs/wp-config.php"
 text=open(filename).read()
 open(filename,"w").write(text.replace("database_name_here",""+domainName+'_db'))

 filename="/var/www/"+domainName+"/htdocs/wp-config.php"
 text=open(filename).read()
 open(filename,"w").write(text.replace("username_here","root"))

 filename="/var/www/"+domainName+"/htdocs/wp-config.php"
 text=open(filename).read()
 open(filename,"w").write(text.replace("password_here",""+rootpass))

 os.system('sudo service nginx reload')
 os.system('sudo /etc/init.d/mysql restart')
 os.system('sudo /etc/init.d/php5-fpm restart ')

 print('\n\nEverythings set, please open'+' '+domainName+' '+'in your browser!' )

# close the application
app.close()
