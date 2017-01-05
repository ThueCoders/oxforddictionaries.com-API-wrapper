# oxforddictionaries.com-API-wrapper
Simple wrapper for oxforddictionaries.com API


```python
>>> from oxforddict import OxfordDictionary
>>> d = OxfordDictionary(app_key="your key", app_id="your id")
>>> d.sentences('cat') # returns dict with result
{'results': [{'word': 'cat', 'lexicalEntries': [...

>>> d.entries('true', 'examples')
{'metadata': {'provider': 'Oxford University Press'}, 'results': [{'type':....

```