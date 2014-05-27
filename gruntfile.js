module.exports = function (grunt) {
    'use strict';
    require('load-grunt-tasks')(grunt, {scope: 'devDependencies'});

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        /**
         * Builds SASS source files to CSS.
         *
         * Watches for changes during development to auto-build.
         * Compiles compressed CSS for production.
         */
        compass: {
            options: {
                sassDir: './demo/scss',
                cssDir: './demo/static/css',
                importPath: './bower_components/foundation/scss'
            },

            prod: {
                options: {
                    environment: 'production',
                    outputStyle: 'compressed'
                }
            },

            watch: {
                options: {
                    environment: 'development',
                    outputStyle: 'expanded',
                    watch: true
                }
            }
        },

        /**
         * Runs watch tasks concurrently for non-blocking watch.
         */
        concurrent: {
            dev: {
                tasks: ['compass:watch'],
                options: {
                    logConcurrentOutput: true
                }
            }
        },
    });

    grunt.registerTask('default', ['concurrent']);
    grunt.registerTask('build', ['compass:prod']);
};
