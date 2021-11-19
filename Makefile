website:
	aws s3 cp app/website/ s3://crosschecker.app --recursive	
	#invalidate cloudfront cache. need to programmatically grab distribution id in the future
	aws cloudfront create-invalidation --distribution-id E16ECMN8EZ6P9I --paths "/*" 2>&1 > /dev/null
