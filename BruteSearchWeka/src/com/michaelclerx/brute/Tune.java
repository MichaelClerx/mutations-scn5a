package com.michaelclerx.brute;

import java.io.PrintWriter;
import java.util.ArrayList;

public class Tune
{
	public final static boolean debug = false;

	public static void main(String[] args) throws Exception
	{
		//String meth = "random-forest";		// Done
		//String meth = "naive-bayes";		// Done 
		String meth = "mlp";				// Done
		//String meth = "svm";				// Done 
		//String meth = "knn";				// Done
		//String[] datasets = { "changed", "act", "inact", "late", "zero" };
		String[] datasets = { "dvi-disc" };
		Spec spec;
		if (meth == "random-forest") {
			spec = RandomForest();
		} else if (meth == "naive-bayes") {
			spec = NaiveBayes();
		} else if (meth == "mlp") {
			spec = MLPClassifier();
		} else if (meth == "svm") {
			spec = LibSVM();
		} else if (meth == "knn") {
			spec = IBk();
		} else {
			throw new Exception("Unknown method.");
		}
		if (debug) {
			//spec = MLPClassifier();
			spec = LibSVM();
		}

		for (String data : datasets) {
			System.out.println("TUNING TUNING TUNING TUNING TUNING TUNING TUNING");
			System.out.println("Method: " + meth);
			System.out.println("Data  : " + data);
			System.out.println();
			
			// MCC or AUC
			boolean mcc = data.equals("dvi-disc") ? false : true;
			System.out.println("Selecting on " + (mcc ? "MCC" : "AUC"));

			// Explore
			Explorer e = new Explorer(data + ".arff", spec, mcc);
			ArrayList<Solution> solutions = e.run();

			System.out.println();
			System.out.println();

			// Store
			String filename = data + "-" + meth + ".txt";
			System.out.println("Writing to " + filename);
			PrintWriter writer = new PrintWriter(filename, "UTF-8");
			for (Solution solution : solutions) {
				writer.println("MCC: " + solution.mcc);
				writer.println("AUC: " + solution.auc);
				writer.println("Acc: " + solution.acc);
				writer.println(spec.classifier + " " + solution.option);
				writer.println();
			}
			writer.close();
			System.out.println("Done with " + data);

			System.out.println();
			System.out.println();

			if (debug) {
				break;
			}
		}
		System.out.println("Completely done!");
	}

	private static Spec RandomForest()
	{
		Spec spec = new Spec("weka.classifiers.trees.RandomForest");

		for (int bagSize = 4; bagSize <= 100; bagSize += 4) {
			for (int randFeat = 0; randFeat <= 10; randFeat++) {
				for (int iter = 20; iter <= 100; iter += 10) {
					// Disable "break ties randomly"
					spec.add("-P", bagSize, "-K", randFeat, "-I", iter);

					// Enable "break ties randomly"
					spec.add("-P", bagSize, "-K", randFeat, "-I", iter, "-B");
				}
			}
		}

		return spec;
	}

	private static Spec NaiveBayes()
	{
		Spec spec = new Spec("weka.classifiers.bayes.NaiveBayes");
		spec.add("");
		spec.add("-K");
		spec.add("-D");
		return spec;
	}

	private static Spec MLPClassifier()
	{
		Spec spec = new Spec("weka.classifiers.functions.MLPClassifier");

		int ilo, ihi, jlo, jhi, nhi;
		if (debug) {
			nhi = 2;
			ilo = 1;
			ihi = 3;
			jlo = 5;
			jhi = 8;
		} else {
			nhi = 10;
			ilo = 1;
			ihi = 10;
			jlo = 1;
			jhi = 10;
		}

		for (int n = nhi; n > 1; n--) {
			for (int i = ilo; i < ihi; i++) {
				for (int j = jlo; j < jhi; j++) {
					double r = Math.pow(10, -i);
					double t = Math.pow(10, -j);
					spec.add("-N", n, "-R", r, "-O", t, "-P", 1, "-E", 1, "-S", 1, "-L",
							"weka.classifiers.functions.loss.SquaredError", "-A",
							"weka.classifiers.functions.activation.ApproximateSigmoid");
				}
			}
		}

		return spec;
	}

	private static Spec LibSVM()
	{
		Spec spec = new Spec("weka.classifiers.functions.LibSVM");

		int clo = 0, chi = 10;
		int glo = -25, ghi = -5;
		if (Tune.debug) {
			chi = clo + 1;
			ghi = glo + 1;
		}
		
		double cost, gamma;
		for (int c = clo; c < chi; c++) {
			for (int g = glo; g < ghi; g++) {
				cost = Math.pow(2, c);
				gamma = Math.pow(2, g);
				spec.add("-C", cost, "-G", gamma, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			}
		}
		// Degree has no effect

		return spec;
	}

	private static Spec IBk()
	{
		Spec spec = new Spec("weka.classifiers.lazy.IBk");
		String[] distances = new String[] { 
				"ChebyshevDistance",
				"EuclideanDistance", 
				"FilteredDistance",
				"ManhattanDistance", 
				"MinkowskiDistance", 
				};

		for (int k = 1; k < 20; k++) {
			for (String d : distances) {
				d = "weka.core.neighboursearch.LinearNNSearch -A weka.core." + d;

				// Add without distance weighting
				spec.add("-K", k, "-A", d);
				// Add with distance weighting
				spec.add("-K", k, "-F", "-A", d);
				// Add with 1/distance weighting
				spec.add("-K", k, "-I", "-A", d);
			}
		}

		return spec;
	}
}