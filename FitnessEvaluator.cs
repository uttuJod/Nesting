using OpenCvSharp;


class ExternalEvaluator
{
    int canvasHeight;
    int canvasLength;
    int canvasHeight_mm;
    int canvasLength_mm;
    string svgDirectoryPath;
    string bmpDirectoryPath;
    float kerf_mm;
    float kerf;
    float scale;
    float pixel_size; 



    public ExternalEvaluator(string configFilePath)
    {
        InitializeConfig(configFilePath);
    }

    // Method to initialize config
    private void InitializeConfig(string configFilePath)
    {
        kerf_mm = 10.0f; //kerf allowance in mm
        scale = 1.15f; //default value in case of error
        pixel_size = 4.0f; //in mm, size of a single pixel
        canvasHeight_mm = 400;
        canvasLength_mm = 400;
        canvasHeight = canvasHeight_mm / (int)pixel_size;
        canvasLength = canvasLength_mm / (int)pixel_size;
        kerf = kerf_mm/pixel_size; //kerf allowance in mm
        svgDirectoryPath = @"D:\IITB\RM Lab\Nesting_GA\external_dependencies\SVGs";
        bmpDirectoryPath = "D:\\IITB\\RM Lab\\Nesting_GA\\Files\\Dileep_output";
    }

    public double EvaluateChromosomes(string chromosome)
    {
        int numPlaced = 0;
        //int totA = 0;
        int scaledTotA = 0;
        double fitness = 0.000f;
        //int overlapU = -1;
        int overlapS = -1;
        int totalCanvasArea = canvasHeight * canvasLength;
        //int overlapA = 0;
        if (chromosome.Length > 0)
        {

            Mat canvasS = new Mat(canvasHeight, canvasLength, MatType.CV_8UC1, new Scalar(0));
            //Mat canvasU = new Mat(canvasHeight, canvasLength, MatType.CV_8UC1, new Scalar(0));
            int[] X, Y, R;
            ProcessChromosome(chromosome, out X, out Y, out R);

            for (int i = 0; i < X.Length; i++)
            {
                Mat S_temp = new Mat(canvasHeight, canvasLength, MatType.CV_8UC1, new Scalar(0));
                //Mat U_temp = new Mat(canvasHeight, canvasLength, MatType.CV_8UC1, new Scalar(0));

                string bmpFilePath = Path.Combine(bmpDirectoryPath, (i + 1).ToString("D3") + "_00_" + R[i].ToString("D3") + ".bmp");
                Mat bmp = LoadBMP(bmpFilePath);

                /*Cv2.ImShow("BMP", bmp); // Display the image
                Cv2.WaitKey(0); // Wait for a key press
                Cv2.DestroyAllWindows();*/ // Close the window after key press
                //Console.WriteLine($"converted");
                // Check if the BMP is null
                if (bmp == null)
                {
                    Console.WriteLine($"Failed to read BMP {i} for chromosome {chromosome}");
                    continue;
                }

                //Console.WriteLine($" Area {scaledTotA}");
                /*if (bmp != null)
                {
                    PlaceBMPOnCanvas(U_temp, bmp, X[i], Y[i], 1);
                }

                Cv2.BitwiseOr(canvasU, U_temp, canvasU);*/
                //Cv2.ImShow("Canvas", bmp); // Display the image
                //Cv2.WaitKey(0); // Wait for a key press
                //Cv2.DestroyAllWindows();

                //totA += Cv2.CountNonZero(bmp);
                int rows = bmp.Rows, cols = bmp.Cols;

                int min_edge = Math.Min(rows, cols);

                scale = 1+(kerf/((float)min_edge));

                //bmp = ScaleBMP(bmp, scale);
                //Console.WriteLine($" Area {scaledTotA}");
                //int X2 = X[i] - (int)((scale - 1) * X[i] / 2);
                //int Y2 = Y[i] - (int)((scale - 1) * Y[i] / 2);
                if (bmp != null)
                {
                    PlaceBMPOnCanvas(S_temp, bmp, X[i], Y[i], scale);
                    scaledTotA += Cv2.CountNonZero(bmp);
                }

                Cv2.BitwiseOr(canvasS, S_temp, canvasS);
                //Cv2.BitwiseOr(canvasU, U_temp, canvasU);
                //overlapA += Cv2.CountNonZero(canvasU);
                //Console.WriteLine($"{overlapA}, {totA}");

                // Display the canvas using OpenCV
            }

            //Cv2.ImShow("Canvas", canvasS); // Display the image
            //Cv2.WaitKey(0); // Wait for a key press
            //Cv2.DestroyAllWindows();

            //overlapU = (totA - Cv2.CountNonZero(canvasU));
            overlapS = (scaledTotA - Cv2.CountNonZero(canvasS));
            //Console.WriteLine($"Overlap:{totA}, {Cv2.CountNonZero(canvasU)}");
            //Console.WriteLine($"Overlap:{overlapS}");
            if (overlapS > 0)
            {
                fitness = -(overlapS);
            }
            else if (overlapS<=0) {

                int l2 = canvasS.Cols;
                int l1 = 0;
                for (int col = 0; col <l2; col++) // Start from the first column and move right
                {
                    // Extract the column as a Mat
                    Mat column = new Mat(canvasS, new Rect(col, 0, 1, canvasS.Rows)); // Extract a single column

                    // Count the number of non-zero pixels in the column
                    if (Cv2.CountNonZero(column) > 0)
                    {
                        l1 = col;
                        break;
                    }
                }
                for (int col = l2 - 1; col >= l1; col--) // Start from the last column and move left
                {
                    // Extract the column as a Mat
                    Mat column = new Mat(canvasS, new Rect(col, 0, 1, canvasS.Rows)); // Extract a single column

                    // Count the number of non-zero pixels in the column
                    if (Cv2.CountNonZero(column) > 0)
                    {
                        l2 = col;
                        break;
                    }
                }
                fitness = (l1+(canvasS.Cols-l2)); 
            }
            return fitness;
        }
        else
        {
            Console.WriteLine("No data found in the CSV.");
            return -1;
        }

        //Console.WriteLine("Chromosome evaluation completed.");
    }


    // Method to process a chromosome and extract X, Y, and R
    private void ProcessChromosome(string chromosome, out int[] X, out int[] Y, out int[] R)
    {
        var values = chromosome.Split(',').Select(int.Parse).ToArray();
        int numGenes = values.Length / 3 ;
        X = new int[numGenes];
        Y = new int[numGenes];
        R = new int[numGenes];

        for (int i = 0; i < numGenes; i++)
        {
            X[i] = values[i * 3];
            Y[i] = values[i * 3 + 1];
            R[i] = values[i * 3 + 2];
        }

    }

    //Method to load BMP in grayscale and invert it, based on the filepath
    private Mat LoadBMP (string bmpFilePath)
    {

        Mat bmpImage = Cv2.ImRead(bmpFilePath, ImreadModes.Grayscale);
        Cv2.BitwiseNot(bmpImage, bmpImage);
        return bmpImage;
    }

    // Method to scale the BMP about the center
    /*private Mat ScaleBMP(Mat image, float scale)
    {
        float scaleFactor = scale; // Example scale factor, can be adjusted based on kerf allowance
        Size newSize = new Size(image.Width * scaleFactor, image.Height * scaleFactor);
        Mat scaledImage = new Mat();
        Cv2.Resize(image, scaledImage, newSize, image.Width/2, image.Height/2, InterpolationFlags.Linear);
        return scaledImage;
    }*/

    // Method to place the BMP on the temporary canvas
    private void PlaceBMPOnCanvas(Mat canvas, Mat bmp, int x, int y, float scale)
    {
        /*//Cv2.ImShow("BMP", bmp);
        //Cv2.WaitKey(0);
        // Iterate over each pixel of the BMP
        for (int i = 0; i < bmp.Height; i++)
        {
            for (int j = 0; j < bmp.Width; j++)
            {
                // Calculate the target position on the canvas
                int canvasX = x + j;
                int canvasY = y + i;
                //Console.WriteLine($"{canvasX}, {canvasY}");
                // Check if the pixel is within the canvas bounds
                if (canvasX < canvas.Width && canvasY < canvas.Height && canvasX >=0 && canvasY>=0)
                {
                    // Copy the pixel from the BMP to the canvas
                    byte bmpPixel = bmp.At<byte>(i, j);  // For grayscale images
                    canvas.Set<byte>(canvasY, canvasX, bmpPixel);
                }
            }
        }*/
        // Define full ROI (Region of Interest) where BMP should be placed
        Rect bmpRect = new Rect(x, y, bmp.Width, bmp.Height);
        Rect canvasRect = new Rect(0, 0, canvas.Width, canvas.Height);

        // Compute intersection (ensures only in-bounds pixels are used)
        Rect validROI = bmpRect & canvasRect;

        if (validROI.Width > 0 && validROI.Height > 0) // Ensure there’s a valid region to place
        {
            // Extract valid regions from BMP and Canvas
            Mat canvasROI = new Mat(canvas, validROI);
            Mat bmpROI = new Mat(bmp, new Rect(validROI.X - x, validROI.Y - y, validROI.Width, validROI.Height));

            // Perform efficient bitwise OR only on the valid region
            Cv2.BitwiseOr(canvasROI, bmpROI, canvasROI);
        }

        //Cv2.ImShow("Canvas", canvas); // Display the image
        //Cv2.WaitKey(10); // Wait for a key press
        //Cv2.DestroyAllWindows();
    }

}

class Program
{
    static void Main(string[] args)
    {
        try
        {
            //Console.WriteLine("Starting evaluation...");

            string configFilePath = "path_to_config.txt";

            // Initialize the evaluator with the config file
            ExternalEvaluator evaluator = new ExternalEvaluator(configFilePath);

            // Evaluate chromosomes using input and output CSV paths
            double fitness = evaluator.EvaluateChromosomes(args[0]);

            //Console.WriteLine("Evaluation completed.");

            Console.WriteLine(fitness);
        }
        catch (Exception ex)
        {
            Console.WriteLine("An error occurred: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
        }

        //Keep the console open so you can see the output
        //Console.WriteLine("Press Enter to close...");
        //Console.ReadLine();
    }

}
