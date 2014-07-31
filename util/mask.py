import re

def mask_to_re(mask):
	return re.compile(re.escape(mask).replace(r"\*", ".+").replace(r"\?", "."))

def match(mask, prefix):
	return mask_to_re(mask).match(prefix)
