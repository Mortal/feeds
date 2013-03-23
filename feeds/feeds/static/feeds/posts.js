function swap_form(form) {
    var btn = form.submit_button;
    var cur_action = ""+form.getAttribute('action');
    var cur_label = ""+btn.getAttribute('value');
    var new_action = ""+form.getAttribute('data-alt-action');
    var new_label = ""+form.getAttribute('data-alt-label');
    var new_state = ""+form.getAttribute('data-new-state');
    var old_state = (new_state == 'read') ? 'unread' : 'read';
    var post = form;
    while (post && !post.classList.contains('post')) post = post.parentNode;
    post.classList.remove(old_state);
    post.classList.add(new_state);
    setTimeout(function () {
        form.setAttribute('action', new_action);
        btn.setAttribute('value', new_label);
        form.setAttribute('data-alt-action', cur_action);
        form.setAttribute('data-alt-label', cur_label);
        form.setAttribute('data-new-state', old_state);
    }, 0);
    return true;
}
