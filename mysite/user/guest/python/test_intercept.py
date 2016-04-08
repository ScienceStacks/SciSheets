
# Simple test to verify the code
if __name__ == "__main__":
  SIZE = 100
  INTERCEPT = 5
  SLOPE = 3
  SD = 1.0
  xarray = np.array(range(SIZE), dtype=float)
  yarray = INTERCEPT + SLOPE*xarray + sp.random.normal(0, SD, SIZE)
  computed_intercept = intercept(xarray, yarray)
  if abs(computed_intercept[0] - INTERCEPT) < 4*SD/np.sqrt(SIZE):
    print ("OK.")
  else:
    print ("Validation failed!")
