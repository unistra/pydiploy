if !has('python')
    finish
endif

function! InsertFabfileBottle()

    if filereadable($HOME."/.vim/bundle/pydiploy-vim/plugin/insertfabfilebottle.py")
        pyfile $HOME/.vim/bundle/pydiploy-vim/plugin/insertfabfilebottle.py
    elseif filereadable($HOME."/.vim/plugin/insertfabfilebottle.py")
        pyfile $HOME/.vim/plugin/insertfabfilebottle.py
    else
        call confirm("Error: insertfabfilebottle.py cannot be found! Please reinstall the plugin", 'OK')
        finish
    endif
    :e
endfunc

command! PYDIPLOYFABBOTTLE call InsertFabfileBottle()
