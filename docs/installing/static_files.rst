Aristotle Static Files
======================

Webpack
-------

Aristotle uses webpack to bundle most static files served on the site. We also use webpack to compile .less stylesheets and to compile es6 javascript into backwards compatible versions using babel. More information about weback can be found here: https://webpack.js.org/

Arisotle Webpack Structure
--------------------------

The webpack project lives under /assets in the mono-repo. All pages with different js or css should have their own webpack entrypoint. All files in /src/pages are treated as entrypoints. /src/lib is for custom js that is used across entrypoints. /src/styles is where all the .css and .less stylesheets are found and src/components are where single file vue components are found

During Development
------------------

When making changes to aristotle we recommend using docker-compose to run your development version. This will automatically run the webpack build for you whenever a file is updated. The contianer will need to be restarted when adding a new page or changing the webpack config. This can be done with the `docker-compose restart webpack` command

Note that slightly different webpack configuration is used in development. The common, dev and prod configs can be found in /assets

If you wish to see what is in each of the generated bundles you can view the report generated with each build. This can be found at /assets/dist/report.html and gives a graphical represantaion of the bundles

Installing Dependancies
-----------------------

We use npm for dependancy management. You can run `npm install` from the assets directory to install all dependancies. This is not neccessary when using docker-compose

Running Builds
--------------

If you want to run a production build you can run `npm run build`. For a continuously updating development build you can run `npm run watch`

Bundle Loading
--------------

Bundles are loaded into the django template using django-webpack-loader. This provides some simple template tags to load the bundles. The css and js bundles should be loaded in the webpack_bundle and webpack_css_bundle blocks defined in base.html. See sandbox.html for an example

Testing
-------

Front end tests are written using the mocha framework and chai assertion library and can be found in /assets/test.
The tests are also processed with webpack before being executed by the karma test runner.

You can run the tests with `npm run test`. They are also executed by travis on each pull request

Linting (Style Checking)
------------------------

Our package.json file contains some eslint configuration for style checking. Eslint can be run with `npm run lint`
