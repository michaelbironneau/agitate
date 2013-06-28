#Agitate - Generic CMS Frontend using Git
Author: Michael Bironneau (@MikeBrno)

##Introduction
Agitate combines the power and version control of GIT with the flexibility of web APIs. It allows you to manage content for any website that has an adequate API with CRUD methods and push those changes to a git repo with a git-like interface. You create a GIT repo for your content using an intuitive folder structure (/model/resource) and use Agitate to manage your repo, using the exact same commands as GIT. The only difference is that every time you commit (unless using the --dry-run option), Agitate creates the appropriate requests to your backend's API to update the content.

You get version control, the ability to rollback changes, and a basic ORM that understands one-to-one and many-to-one relationships. If you make changes to a file on your desktop and commit those changes, they will be immediately reflected on your website using the API. It's the perfect way for developers to administer CMSes for their personal websites without having to write a single line of code.

*Agitate follows the same naming conventions as Laravel's Eloquent ORM for models and foreign keys.*

##Basic Usage Instructions
The basic structure that Agitate understands is model-resource. For example, in a blog a model could be "Article" and a resource could be your first article. One would expect to find an Article resource at

    http://www.yoursite.com/api/Articles/{id or slug}

Agitate requires a specific folder structure for your content to mirror that structure which is present on your site:

    Models/[filename].yaml

It is important that the folder name corresponding to the model [Model] be [Model]s . This is where Agitate will look for resources. Within the [Model]s directory, resources are marked up using YAML, which basically looks like this:

    field1: value1
    field2: value2

If you are not familiar with YAML I suggest looking [here](http://www.keleshev.com/yaml-quick-intoduction) for an introduction.

*Capitalization in field names is important*

###What the requests will look like
Agitate can be configured to make requests using any of HTTP POST, PUT, or DELETE. The URL the requests are made to can be specified, but it is recommended that your API accept the following requests:

**Creation: POST request to**

    http://yourserver/path-to-api/[model]/

**Updating: PUT request to**

    http://yourserver/path-to-api/[model]/[resource-id]

**Deletion: DELETE request to**

    http://yourserver/path-to-api/[model]/[resource-id]

####Expected Server Response

In the event of a successful update or deletion, Agitate expects an HTTP response with status code between 200 and 299, endpoints included. Any status code outside this range will be treated as an unsuccessful interaction.

Agitate also expects to receive a resource ID as part of the response to successful creation requests. This response is expected to be JSON-encoded. The resource-id need not have a specific key name, Agitate will simply look for the first numeric value it encounters in the response body and treat this as the id. *Currently, if your API's response body for successful creation requests contains more than one numeric value, this may cause conflicts. This will be fixed in subsequent releases*

###Including files
You may want to upload files with your resource. For example, if your content consists of blog posts, perhaps you want to upload thumbnails or images. Or perhaps the text of your blog posts is Markdown and you want to store it in a separate file. Agitate comes with two mixins @file and @content that deal with these situations.

####@file
This specifies that the referred file should be uploaded as part of the request. Your website then accesses these through the $_FILES (if using PHP). The syntax is as follows:

    field-name: "@file(path-relative-to-resource)"

Note that the quotation marks are important to avoid YAML syntax errors due to the @ symbol.

####@content
This mixin specifies that the chosen field's data is stored in a different file. For example, if your resources are athlete profiles and one data field is a long text biography formatted with Markdown, it may be more convenient for you to store it in a different file. The syntax for specifying this is:

    field-name: "@content(path-relative-to-resource)"

Note that the quotation marks are important to avoid YAML syntax errors due to the @ symbol.

###Dependency Management
Agitate keeps track of which resources depend on which files. If you change a file, Agitate will update the resources that depend on it next time you commit, even if the resource YAML file hasn't changed.

##Object Relationships
The current version of Agitate supports one-to-one and many-to-one relationships. For example, a Client model might have a Phone. In the database, this relationship is usually highlighted with the use of a foreign key. Following the conventions of popular PHP framework Laravel, Agitate assumes that this field, in table Client, will be named Phone_id, or that the field, in table Phone, is named Client_id. We will soon see how to specify both kinds.

In a many-to-one relationship, an object can have many dependents. For example, a blog post can have many comments. Again, Agitate assumes that the foreign key field in the Comments table will be named Phone_id.

The way to specify the dependence is the @[model-name] field, where @[model-name] is the name of the model that has the foreign key. The syntax is as follows:

    "@Model-name" : filename-of-resource

if the foreign key is in the table of the model for the current resource (the one whose YAML file you are writing this in), or, if the foreign key is in the model name who you are specifying, then use ">" to indicate this:

    "@Model-name >" : filename-of-resource

For example, for the Client/Phone example there might be a line in client1.yaml that looks like this:

    "@Phone" : iPhone

Many-to-one relationships should be specified as a list, i.e.

    "@Comments" : [comment1, comment2, comment3]

Note that the model name on the left hand side after the "@" is plural! Agitate will automatically assume that the foreign key is in the Phone table, there is no need to write ">" (though it will not produce an error, either).

If there was only one phone per client and you wanted to store the foreign key in the Phone table, then instead write

    "@Phone >" : iPhone

**Important:**
Note that the value on the right hand side is not a path, it is the filename of the resource. In the above example, Agitate already knows to look in the Phones/ directory to find iPhone3GS.yaml. Appending the extension is not necessary either.

##Errors

Agitate is verbose by default and will let you know about all the problems that it encounters in updating your content via your web API. If no errors are encountered, Agitate will return control to Git to perform the commit. If there are errors, you will be prompted whether you still want to continue with the commit and it will be possible to abort it.

***It is strongly recommended that you do not proceed with a commit that was unsuccesful for Agitate otherwise the content on your server and in your repository may become out of sync***

####Examples of errors:

Malformed YAML, broken links in @file or @content, file permission errors (the [model]/ directories should be writeable), internal server errors, method not allowed error (especially if using PUT/DELETE).

These errors will be returned to stdout with more information. It is outside the scope of this readme to explain the meaning of all these errors, especially since Agitate is intended for use by developers in the first place.