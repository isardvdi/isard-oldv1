import glob, os
root_dir='../../templates/'
js=[]
jsadmin=[]
css=[]
cssadmin=[]
for filename in glob.iglob(root_dir + '**/*.html', recursive=True):
    if 'classroom' in filename: continue
    comment=False
    for line in open(filename,'r'):
        if '<!--' in line and '-->' in line: 
            continue
        if '<!--' in line and not '-->' in line: 
            comment = True
            continue
        if comment and '-->' not in line: 
            continue
        if comment and '-->' in line:
            comment = False
            continue
        line.replace('`',"'")

            
        if '.js' in line:
            try:
                
                path=line.strip().split("src=")[1].split(">")[0].strip('"')
                if path.startswith('//'): 
                    continue
                if path.startswith('..'): 
                    continue
                if path.startswith('http'): 
                    continue
                if path.startswith('/'): path=path[1:]
                if path.startswith('vendors'): path='bower_components/gentelella/'+path
                if path.startswith('build'): path='bower_components/gentelella/'+path
                if path.startswith('admin'): path='static/'+path
                if path.startswith('js'): path='static/'+path
                # ~ if path.startswith('bower_components'): path='static/bower_components/'+path
                if path.startswith('font-linux'): path='static/bower_components/font-linux/assets/'+path.split('/')[-1]
                if '/admin/' not in filename: 
                    js.append(path)
                jsadmin.append(path)
            except:
                print('ERROR')
                print(filename)
                print(line)

        if '.css' in line:
            try:
                
                path=line.strip().split("href=")[1].split('"')[1].strip('"')
                if path.startswith('//'): 
                    continue
                if path.startswith('..'): 
                    continue
                if path.startswith('http'): 
                    continue
                if path.startswith('/'): path=path[1:]
                if path.startswith('vendors'): path='bower_components/gentelella/'+path
                if path.startswith('build'): path='bower_components/gentelella/'+path
                if path.startswith('font-linux'): path='bower_components/font-linux/assets/'+path.split('/')[-1]
                if '/admin/' not in filename: 
                    css.append(path)
                cssadmin.append(path)
            except:
                print('ERROR')
                print(filename)
                print(line)
# ~ import pprint
# ~ pprint.pprint(css)
# ~ pprint.pprint(cssadmin)
                
listjs=set(js)
datajs=[]
for l in listjs:
    datajs.append('../../'+l)

listjsadmin=set(jsadmin)
datajsadmin=[]
for l in listjsadmin:
    datajsadmin.append('../../'+l)


listcss=set(css)
datacss=[]
for l in listcss:
    datacss.append('../../'+l)

listcssadmin=set(cssadmin)
datacssadmin=[]
for l in listcssadmin:
    datacssadmin.append('../../'+l)


### TEST FILE EXISTS  
ejs=[]  
for d in datajs:
    if not os.path.isfile(d):
        ejs.append(d)
if len(ejs):
    print('ERROR IN JS PATHS')
    print(ejs)

ejs=[]  
for d in datajsadmin:
    if not os.path.isfile(d):
        ejs.append(d)
if len(ejs):
    print('ERROR IN ADMIN JS PATHS')
    print(ejs)
    
ejs=[]  
for d in datacss:
    if not os.path.isfile(d):
        ejs.append(d)
if len(ejs):
    print('ERROR IN CSSS PATHS')
    print(ejs)
    
ejs=[]  
for d in datacssadmin:
    if not os.path.isfile(d):
        ejs.append(d)
if len(ejs):
    print('ERROR IN ADMINCSS PATHS')
    print(ejs)
                    
gulpfile='''
// including plugins

var gulp = require('gulp'),
    minifyCSS = require('gulp-minify-css'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    prefix = require('gulp-autoprefixer');

var app = {};
app.addScript = function(paths, outputFilename) {
    return gulp.src(paths)
        .pipe(concat(outputFilename)) // concat files
        .pipe(uglify().on('error', function(e){
            console.log(e);
         }))
        .pipe(gulp.dest('../../static/isard'));
};

gulp.task('isard-user-js', function () {
    app.addScript(%s,'isard-user.js');
})

gulp.task('isard-admin-js', function () {
    app.addScript(%s,'isard-admin.js');
})


app.addStyle = function(paths, outputFilename) {
    return gulp.src(paths)
    .pipe(concat(outputFilename))
    .pipe(minifyCSS())
    .pipe(prefix('last 2 versions'))
    .pipe(gulp.dest('../../static/isard'))
};

gulp.task('isard-user-css', function () {
    app.addStyle(%s,'isard-user.css');
})

gulp.task('isard-admin-css', function () {
    app.addStyle(%s,'isard-admin.css');
})



gulp.task('default', function() {
    gulp.run('isard-user-js')
    gulp.run('isard-admin-js')
    gulp.run('isard-user-css')
    gulp.run('isard-admin-css')
});

''' % (datajs, datajsadmin, datacss, datacssadmin)
# ~ (', '.join(list))

with open('gulpfile.js', 'w') as dest:
    dest.write(gulpfile)
