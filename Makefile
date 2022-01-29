# Upload the static website and invalidate the CloudFront cache so that changes can be seen without waiting
website:
	aws s3 cp app/website/ s3://crosschecker.app --recursive	
	#invalidate cloudfront cache. need to programmatically grab distribution id in the future
	aws cloudfront create-invalidation --distribution-id E16ECMN8EZ6P9I --paths "/*" 2>&1 > /dev/null

# Upload application code for lambda functions
lambdas:
	zip -rj app/lambdas/image-uploader-generate-signature.zip app/lambdas/image-uploader-generate-signature
	aws s3 cp app/lambdas/image-uploader-generate-signature.zip s3://crosschecker.app-lambda-functions
	aws lambda update-function-code --function-name crosschecker-image-uploader-generate-signature --s3-bucket crosschecker.app-lambda-functions --s3-key image-uploader-generate-signature.zip > /dev/null

# Download raw user-uploaded data from main crosschecker.app
raw_images:
	aws s3 sync s3://crosschecker.app-data/image_uploads/ ml_model/data/raw/image_uploads

# Download the cached crosswords from s3
answer_keys:
	aws s3 sync s3://crosschecker.app-data/nyt_answer_keys/ ml_model/data/raw/nyt_answer_keys

# Web app to help with labelling data
labeler:
	# limitation of MAKE requires setting variable and running flask on same line
	FLASK_APP=app/data_labeler/app.py flask run

make_dataset:
	python ml_model/src/data/make_dataset.py