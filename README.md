# NYT Cross Check

An app for checking the answers of your printed New York Times Crossword puzzle.

[Demo](https://crosschecker.app)


## TODO

## Lambdas
- Download NYT answer key in lambda

### Website
- Capture/upload only square grid image - full aspect ratio is uploading unneeded data and slowing things down.

### ML Model
- Try Hough transform for grid lines
- Improve slicing algorithm to work on grids of different sizes and inputs of different sizes (don't hardcode unique horizontal/vertical line pixels)