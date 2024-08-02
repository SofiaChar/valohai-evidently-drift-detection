import urllib.request
import urllib.parse
import valohai

urllib.request.urlopen(urllib.request.Request(
   'https://app.valohai.com/api/v0/launch/0190fe82-c984-5f66-8302-69874914e1c9/',
   data=urllib.parse.urlencode({
      'hello': 'valohai',
      'dataset': valohai.parameters('dataset_path').value
   }).encode(),
   headers={
      'Authorization': 'secret=hYy67rJDgaSc8XGZpgKNuRnZVkCpoGy1QksBPb2Q'
   }
))
