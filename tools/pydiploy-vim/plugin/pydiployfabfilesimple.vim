if !has('python')
    finish
endif

function! InsertFabfileSimple()

    if filereadable($HOME."/.vim/bundle/pydiploy-vim/plugin/insertfabfilesimple.py")
        pyfile $HOME/.vim/bundle/pydiploy-vim/plugin/insertfabfilesimple.py
    elseif filereadable($HOME."/.vim/plugin/insertfabfilesimple.py")
        pyfile $HOME/.vim/plugin/insertfabfilesimple.py
    else
        call confirm("Error: insertfabfilesimple.py cannot be found! Please reinstall the plugin", 'OK')
        finish
    endif
    :e
endfunc

command! PYDIPLOYFABSIMPLE call InsertFabfileSimple()
