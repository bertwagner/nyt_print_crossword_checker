website:
	aws s3 cp app/website/ s3://crosschecker.app --recursive	
	#invalidate cloudfront cache. need to programmatically grab distribution id in the future
	aws cloudfront create-invalidation --distribution-id E16ECMN8EZ6P9I --paths "/*" 2>&1 > /dev/null

lambdas:
	zip -rj app/lambdas/image-uploader-generate-signature.zip app/lambdas/image-uploader-generate-signature
	aws s3 cp app/lambdas/image-uploader-generate-signature.zip s3://crosschecker.app-lambda-functions
	aws lambda update-function-code --function-name crosschecker-image-uploader-generate-signature --s3-bucket crosschecker.app-lambda-functions --s3-key image-uploader-generate-signature.zip > /dev/null