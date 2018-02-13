
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
    app.addScript(['../../static/vendor/socket.io.min.js', '../../bower_components/gentelella/vendors/bootstrap-progressbar/bootstrap-progressbar.min.js', '../../static/js/quota.js', '../../bower_components/gentelella/vendors/bootstrap/dist/js/bootstrap.js', '../../bower_components/gentelella/vendors/select2/dist/js/select2.full.min.js', '../../static/js/desktops.js', '../../static/js/restful.js', '../../static/js/snippets/domain_hardware.js', '../../bower_components/gentelella/vendors/echarts/dist/echarts.min.js', '../../static/js/snippets/profile_graphs.js', '../../static/js/snippets/domain_genealogy.js', '../../static/js/viewer.js', '../../bower_components/gentelella/vendors/iCheck/icheck.min.js', '../../bower_components/gentelella/vendors/switchery/dist/switchery.min.js', '../../static/js/snippets/domain_derivates.js', '../../static/isard.js', '../../static/js/snippets/domain_graphs.js', '../../static/js/snippets/alloweds.js', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.confirm.js', '../../static/js/quota_socket.js', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.buttons.js', '../../bower_components/gentelella/vendors/iCheck/icheck.js', '../../static/js/templates.js', '../../bower_components/gentelella/vendors/moment/min/moment.min.js', '../../bower_components/gentelella/vendors/parsleyjs/dist/parsley.min.js', '../../bower_components/gentelella/vendors/validator/validator.js', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.js', '../../bower_components/gentelella/vendors/nprogress/nprogress.js', '../../bower_components/gentelella/vendors/datatables.net-bs/js/dataTables.bootstrap.js', '../../static/js/snippets/quota.js', '../../static/js/disposables.js', '../../bower_components/gentelella/vendors/ion.rangeSlider/js/ion.rangeSlider.min.js', '../../bower_components/gentelella/vendors/jquery/dist/jquery.min.js', '../../bower_components/gentelella/vendors/jquery/dist/jquery.js', '../../bower_components/gentelella/vendors/datatables.net/js/jquery.dataTables.js'],'isard-user.js');
})

gulp.task('isard-admin-js', function () {
    app.addScript(['../../static/vendor/socket.io.min.js', '../../static/admin/js/users.js', '../../static/admin/js/hypervisors.js', '../../bower_components/gentelella/vendors/bootstrap/dist/js/bootstrap.min.js', '../../bower_components/gentelella/vendors/dropzone/dist/min/dropzone.min.js', '../../bower_components/gentelella/vendors/bootstrap-progressbar/bootstrap-progressbar.min.js', '../../static/js/quota.js', '../../bower_components/gentelella/vendors/bootstrap/dist/js/bootstrap.js', '../../bower_components/gentelella/vendors/select2/dist/js/select2.full.min.js', '../../static/js/desktops.js', '../../static/js/restful.js', '../../static/admin/js/graphs/bubblesv3.js', '../../static/js/snippets/domain_hardware.js', '../../static/admin/js/config.js', '../../bower_components/gentelella/vendors/echarts/dist/echarts.min.js', '../../static/js/snippets/profile_graphs.js', '../../static/admin/js/updates.js', '../../static/js/snippets/domain_genealogy.js', '../../static/admin/js/graphs/graphs.js', '../../static/js/viewer.js', '../../static/admin/js/groups.js', '../../static/admin/js/domains.js', '../../bower_components/gentelella/vendors/iCheck/icheck.min.js', '../../bower_components/gentelella/vendors/switchery/dist/switchery.min.js', '../../static/js/snippets/domain_derivates.js', '../../static/isard.js', '../../static/js/snippets/domain_graphs.js', '../../static/js/snippets/alloweds.js', '../../static/admin/js/domains_installs.js', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.confirm.js', '../../static/js/quota_socket.js', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.buttons.js', '../../bower_components/gentelella/vendors/iCheck/icheck.js', '../../static/admin/js/hypervisors_detail.js', '../../static/js/templates.js', '../../bower_components/gentelella/vendors/moment/min/moment.min.js', '../../bower_components/gentelella/vendors/parsleyjs/dist/parsley.min.js', '../../bower_components/gentelella/vendors/fastclick/lib/fastclick.js', '../../bower_components/gentelella/vendors/validator/validator.js', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.js', '../../static/admin/js/domains_resources.js', '../../bower_components/gentelella/vendors/nprogress/nprogress.js', '../../static/admin/js/hypervisors_pools.js', '../../static/admin/js/categories.js', '../../static/admin/js/graphs/tree.js', '../../bower_components/gentelella/vendors/datatables.net-bs/js/dataTables.bootstrap.js', '../../static/js/snippets/quota.js', '../../static/js/disposables.js', '../../bower_components/gentelella/vendors/ion.rangeSlider/js/ion.rangeSlider.min.js', '../../bower_components/d3-bower/d3.min.js', '../../bower_components/gentelella/vendors/jquery/dist/jquery.min.js', '../../bower_components/gentelella/vendors/jquery/dist/jquery.js', '../../bower_components/gentelella/vendors/datatables.net/js/jquery.dataTables.js', '../../static/admin/js/roles.js', '../../static/admin/js/media.js'],'isard-admin.js');
})


app.addStyle = function(paths, outputFilename) {
    return gulp.src(paths)
    .pipe(concat(outputFilename))
    .pipe(minifyCSS())
    .pipe(prefix('last 2 versions'))
    .pipe(gulp.dest('../../static/isard'))
};

gulp.task('isard-user-css', function () {
    app.addStyle(['../../bower_components/gentelella/build/css/custom.css', '../../bower_components/gentelella/vendors/font-awesome/css/font-awesome.css', '../../bower_components/gentelella/vendors/font-awesome/css/font-awesome.min.css', '../../bower_components/gentelella/vendors/bootstrap/dist/css/bootstrap.css', '../../bower_components/gentelella/vendors/animate.css/animate.min.css', '../../bower_components/font-linux/assets/font-linux.css', '../../bower_components/gentelella/vendors/ion.rangeSlider/css/ion.rangeSlider.skinFlat.css', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.buttons.css', '../../bower_components/gentelella/vendors/switchery/dist/switchery.min.css', '../../bower_components/gentelella/vendors/normalize-css/normalize.css', '../../bower_components/gentelella/build/css/custom.min.css', '../../bower_components/gentelella/vendors/iCheck/skins/flat/green.css', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.css', '../../bower_components/gentelella/vendors/datatables.net-bs/css/dataTables.bootstrap.css', '../../bower_components/gentelella/vendors/bootstrap/dist/css/bootstrap.min.css', '../../bower_components/gentelella/vendors/ion.rangeSlider/css/ion.rangeSlider.css', '../../bower_components/gentelella/vendors/select2/dist/css/select2.min.css'],'isard-user.css');
})

gulp.task('isard-admin-css', function () {
    app.addStyle(['../../bower_components/gentelella/build/css/custom.css', '../../bower_components/gentelella/vendors/font-awesome/css/font-awesome.css', '../../bower_components/gentelella/vendors/font-awesome/css/font-awesome.min.css', '../../bower_components/gentelella/vendors/bootstrap/dist/css/bootstrap.css', '../../bower_components/gentelella/vendors/animate.css/animate.min.css', '../../bower_components/font-linux/assets/font-linux.css', '../../bower_components/gentelella/vendors/ion.rangeSlider/css/ion.rangeSlider.skinFlat.css', '../../bower_components/gentelella/vendors/dropzone/dist/min/dropzone.min.css', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.buttons.css', '../../bower_components/gentelella/vendors/nprogress/nprogress.css', '../../bower_components/gentelella/vendors/switchery/dist/switchery.min.css', '../../bower_components/gentelella/vendors/normalize-css/normalize.css', '../../bower_components/gentelella/build/css/custom.min.css', '../../bower_components/gentelella/vendors/iCheck/skins/flat/green.css', '../../bower_components/gentelella/vendors/pnotify/dist/pnotify.css', '../../bower_components/gentelella/vendors/datatables.net-bs/css/dataTables.bootstrap.css', '../../static/css/d3-bubble.css', '../../bower_components/gentelella/vendors/bootstrap/dist/css/bootstrap.min.css', '../../bower_components/gentelella/vendors/ion.rangeSlider/css/ion.rangeSlider.css', '../../bower_components/gentelella/vendors/select2/dist/css/select2.min.css'],'isard-admin.css');
})



gulp.task('default', function() {
    gulp.run('isard-user-js')
    gulp.run('isard-admin-js')
    gulp.run('isard-user-css')
    gulp.run('isard-admin-css')
});

