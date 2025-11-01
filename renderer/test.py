from ds_store import DSStore

with DSStore.open('/Users/micfong/Desktop/Test/.DS_Store', 'r+') as d:
  # Position the icon for "Dinner-4.docx" at (1000, 128)
  print(d['Folder 1']['icvp'])

