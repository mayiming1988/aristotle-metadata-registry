$(document).ready(function() {

  var tag_editor = new Taggle('taggle-editor');

  $('#tag-editor-submit').click(function() {
    console.log(tag_editor.getTags().values)
  })

})
