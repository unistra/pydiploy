if !has('python')
    finish
endif

function! InsertFabfile()

    if filereadable($HOME."/.vim/bundle/pydiploy-vim/plugin/insertfabfile.py")
        pyfile $HOME/.vim/bundle/pydiploy-vim/plugin/insertfabfile.py
    elseif filereadable($HOME."/.vim/plugin/insertfabfile.py")
        pyfile $HOME/.vim/plugin/insertfabfile.py
    else
        call confirm("Error: insertfabfile.py cannot be found! Please reinstall the plugin", 'OK')
        finish
    endif
    :e
endfunc

command! PYDIPLOYFAB call InsertFabfile()
