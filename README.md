# NYT Cross Check

An app for checking the answers of your printed New York Times Crossword puzzle.

[Demo](https://crosschecker.app)


## TODO

## Lambdas
- Download NYT answer key in lambda

### Website
- Capture/upload only square grid image - full aspect ratio is uploading unneeded data and slowing things down.
- Do a quick check to see if image will be suitable before uploading?

### ML Model
- Split the difference for hough lines to get the middle of the grid when splitting (although not sure if this will matter - time maybe better spent cleaning up invidual cropped cells?)
- Improve slicing algorithm to work on grids of different sizes and inputs of different sizes (don't hardcode unique horizontal/vertical line pixels)
- Add validation of chopped image - all cells should be roughly same size - erorr out if not, ask user to retake picture