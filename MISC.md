# Misc. errors and solutions

### Font not found (pdflatex)

> Error: Font **** not found

Solution:

- See: https://tex.stackexchange.com/a/129523
- Or just run `updmap`

### Font not found (xelatex)

Same URL as above helped; but command was:

```bash
initexmf --update-fndb
initexmf --edit-config-file updmap
| The latter command should open updmap.cfg in your default editor, commonly Notepad. Add the line below, then save and close.
| Map zi4.map 
| Now in the command window, type
initexmf --mkmaps
updmap
```


### Package `setspace` is not compatible with beamer footnotes

- So we can't have any `setstretch` in the tex