Why is this folder here and what am I supposed to do with it?

Why is this folder here?
------------------------
When you run as localhost over many days, you will eventually lose all of your localhost Datastore data.  I believe it’s intentional. It'll clean up your state periodically due to being a temp file.  Despite being intentional, I find that really annoying.  So this folder ONLY EXIST BECAUSE I FIND IT ANNOYING to lost my localhost data at unexpected times.  Read on if you'd also like to persist localhost data between workdays, or close this README now if you really don't care (which is totally fine).


What do I need to do?
---------------------
To guarentee datastore persistence between localhost runs you need to specify a local folder to use for saving the data.  To do that you need to add the storage_path argument to your Eclipse run arguments so that when Eclipse runs the dev_appserver.py command the argument will be added and point to this folder where Datastore data can be saved.  

For example, in Windows the run argument might look like this:
--storage_path=C:\path\to\this\folder\localhost-storage

On a Mac the run argument might look like this:
 --storage_path=/Users/fisherds/Documents/CSSE480/InstallTest/localhost-storage



How do I set run arguments in Eclipse?
--------------------------------------
First run the project once using the standard right click on the project folder, Run As, PyDev: Google App Run.
Then stop that run. :)  You just wanted to create the basics of the Run Configuration (which is now done)
Next go to the Eclipse run Arguments area.  Click on Run → Run Configurations from the menu.
Then find the specific Run configuration for your app which you just generated from the steps above
Then select the second tab which is called Arguments.
Within the Program Arguments box you will see some "${workspace_loc:ProjectName}" stuff.  Add a space after that stuff and add the --storage_path run argument there as shown above.  For example, on my Mac it might look like this.

"${workspace_loc:InstallTest}" --storage_path=/Users/fisherds/Documents/Rose/CSSE480_AppEngine/myProjects/fisherds-install-test/localhost-storage

Nice work doing the optional stuff. :)