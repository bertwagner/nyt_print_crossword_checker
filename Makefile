deploy:
	aws s3 cp app/ s3://crosscheck-app --recursive	
