package com.michaelclerx.brute;

import weka.core.converters.ArffSaver;
import weka.core.converters.ConverterUtils.DataSource;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Random;

import weka.classifiers.AbstractClassifier;
import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.core.Instances;

/**
 * Brute-force searches a set of parameters (a Spec) for a particular classification method.
 * 
 * Data is split into a training/validation set, and a test set.
 * Tuning is done on the training set, using 10-fold cross-validation to
 * check performance.
 * 
 * A final assessment (after tuning) of classifier performance is made by evaluating
 * on the test set.
 */
public class Explorer
{
	boolean useMcc;
	String file;
	String classifier;
	ArrayList<String[]> options;
	DateTimeFormatter timeFormat = DateTimeFormatter.ofPattern("HH:mm");

	public Explorer(String file, Spec spec, boolean mcc)
	{
		this.file = file;
		this.classifier = spec.classifier;
		this.options = new ArrayList<String[]>(spec.options);
		useMcc = mcc;
	}
	
	/**
	 * Explores all argument options in a spec.
	 * @return
	 */
	public ArrayList<Solution> run()
	{
		// Load and randomise data
		Instances data = getTrainingData();
		int folds = 10;
		Random rand = new Random(1);
		data.randomize(rand);
		if (data.classAttribute().isNominal()) {
			data.stratify(folds);
		}

		//
		// Set up tracking of best solutions
		//
		double bestMcc = -1;
		double bestAuc = 0;
		String[] bestOption = new String[] { "Uninitialised" };
		ArrayList<Solution> solutions = new ArrayList<Solution>();
		if (Tune.debug) {
			solutions.add(new Solution("Terrible", Double.NaN, Double.NaN, Double.NaN, useMcc));
		}

		long start = System.currentTimeMillis();
		double dt, est;
		int j = 0;
		int n = options.size();
		for (final String[] option : options) {
			// Show status
			j++;
			System.out.println("Checking option " + j + " of " + n + ":");
			System.out.println("  " + Spec.formatOption(option));
			System.out.print("  Cross-validating");

			try {
				// Perform cross-validation
				Evaluation eval = new Evaluation(data);
				for (int i = 0; i < folds; i++) {
					String[] optIn = new String[option.length];
					System.arraycopy(option, 0, optIn, 0, option.length);

					System.out.print(".");
					Instances train = data.trainCV(folds, i);
					Instances test = data.testCV(folds, i);

					Classifier cls = AbstractClassifier.forName(classifier, optIn);
					cls.buildClassifier(train);
					eval.evaluateModel(cls, test);
				}

				// Calculate MCC
				double mcc = Double.NaN;
				if (useMcc) {
					mcc = mcc(eval);
	
					// Update best MCC
					if (mcc >= bestMcc) {
						bestMcc = mcc;
						bestOption = option;
					}
				}
				
				// Calculate AUC and accuracy
				double auc = eval.areaUnderROC(0);
				double acc = eval.pctCorrect();
				
				if (!useMcc) {
					// Update best AUC
					if (auc >= bestAuc) {
						bestAuc = auc;
						bestOption = option;
					}
				}					

				// Store solution
				solutions.add(new Solution(Spec.formatOption(option), mcc, auc, acc, useMcc));

				// Show result
				System.out.println("");
				if (useMcc) {
					System.out.println("  MCC : " + mcc);
					System.out.println("  Best: " + bestMcc);
				} else {
					System.out.println("  AUC : " + auc);
					System.out.println("  Best: " + bestAuc);
				}
				//System.out.println("  ACC : " + acc);
				
				// Show estimated time remaining
				dt = (double) (System.currentTimeMillis() - start);
				est = dt * (n - j) / j;
				System.out.println("Estimated time remaining: " + formatTime(est));

			} catch (Exception e) {
				System.out.println("Configuration failed");
				e.printStackTrace();
			}
		}

		if (useMcc) {
			System.out.println("Best MCC: " + bestMcc);
		} else {
			System.out.println("Best AUC: " + bestAuc);
		}
		System.out.println("Best option:");
		System.out.println("  " + Spec.formatOption(bestOption));

		if (Tune.debug) {
			solutions.add(new Solution("Awful", Double.NaN, Double.NaN, Double.NaN, useMcc));
		}
		solutions.sort(new Solution.DescendingComparator());

		return solutions;
	}

	/**
	 * Calculates Matthews Correlation Coefficient (mcc).
	 * @param eval
	 * @return
	 */
	private double mcc(Evaluation eval)
	{
		int classIndex = 0;
		double numTP = eval.numTruePositives(classIndex);
		double numTN = eval.numTrueNegatives(classIndex);
		double numFP = eval.numFalsePositives(classIndex);
		double numFN = eval.numFalseNegatives(classIndex);
		double n = (numTP * numTN) - (numFP * numFN);
		double d = (numTP + numFP) * (numTP + numFN) * (numTN + numFP) * (numTN + numFN);
		d = Math.sqrt(d);

		return n / d;
	}

	/**
	 * Formats a time for status updates.
	 * @param duration
	 * @return
	 */
	private String formatTime(double duration)
	{
		LocalDateTime eta = LocalDateTime.now();
		String out = "";

		duration /= 1000;
		if (duration > 3600) {
			int hours = (int) (duration / 3600);
			duration -= hours * 3600;
			out = hours + "hrs ";
			eta = eta.plusHours(hours);
		}
		if (duration > 60) {
			int minutes = (int) (duration / 60);
			duration -= minutes * 60;
			out += minutes + "min ";
			eta = eta.plusMinutes(minutes);
		}
		int seconds = (int) duration;
		out += seconds + "s";
		eta = eta.plusSeconds(seconds);
		out += " (" + eta.format(timeFormat) + ")";

		return out;
	}
	
	/**
	 * Loads training data.
	 * On first run, data is loaded from a file such as "act.arff" and split into training
	 * and test set. Both sets are saved to disk, and subsequent runs load the existing
	 * training data. 
	 * @return
	 */
	private Instances getTrainingData()
	{
		// Check extension
		if(!file.endsWith(".arff")) {
			System.out.println("Filename must end in .arff");
			System.exit(1);
		}
		
		// Remove extension
		String base = file.substring(0, file.length() - 5);
		String train = base + "-train.arff";
		String test = base + "-test.arff";
		
		if((new File(train)).exists()) {
			// Read training file
			try {
				DataSource source = new DataSource(train);
				Instances data = source.getDataSet();

				// Set class index
				if (data.classIndex() == -1) {
					data.setClassIndex(data.numAttributes() - 1);
				}
				
				return data;
				
			} catch (Exception e) {
				e.printStackTrace();
				System.exit(1);
				return null;
			}
			
		} else {
		    // Read file, split into training and test
			Instances data;
			try {
				DataSource source = new DataSource(file);
				data = source.getDataSet();
			} catch (Exception e) {
				e.printStackTrace();
				System.exit(1);
				return null;
			}
			
			// Set class index
			if (data.classIndex() == -1) {
				data.setClassIndex(data.numAttributes() - 1);
			}

			// Create randomised, stratified sets 
			Random rand = new Random(1);
			data.randomize(rand);
			if (data.classAttribute().isNominal()) {
				data.stratify(3);
			}
			Instances trainingData = data.trainCV(3, 0);
			Instances testData = data.testCV(3, 0);

			// Store
			 try {
				 ArffSaver saver = new ArffSaver();
				 saver.setInstances(trainingData);
				 saver.setFile(new File(train));
				 saver.writeBatch();
				 
				 saver = new ArffSaver();
				 saver.setInstances(testData);
				 saver.setFile(new File(test));
				 saver.writeBatch();
				 				 
			 } catch (IOException e) {
				 e.printStackTrace();
				 System.exit(1);
				 return null;
			 }
			
			 // Return training data
			return trainingData;
		}
	}
	
	/**
	 * Loads test data created by getTrainingInstances().
	 * @return
	 */
	private Instances getTestData()
	{
		// Check extension
			if(!file.endsWith(".arff")) {
				System.out.println("Filename must end in .arff");
				System.exit(1);
			}
				
			// Remove extension
			String base = file.substring(0, file.length() - 5);
			String test = base + "-test.arff";
				
			// Read test file
			try {
				DataSource source = new DataSource(test);
				Instances data = source.getDataSet();
				
				// Set class attribute
				if (data.classIndex() == -1) {
					data.setClassIndex(data.numAttributes() - 1);
				}
				
				return data;
				
			} catch (Exception e) {
				e.printStackTrace();
				System.exit(1);
				return null;
			}
	}
	
	/**
	 * Evaluates the options in a given spec on the test set.
	 * 
	 */
	public void test()
	{
		// Load training data and test data
		Instances trainingData = getTrainingData();
		Instances testData = getTestData();

		// Train and test
		System.out.println("Testing " + classifier + " on " + file);
		for (final String[] option : options) {
			System.out.println("  Checking option: " + Spec.formatOption(option));

			Classifier cls;
			try {
				String[] optIn = new String[option.length];
				System.arraycopy(option, 0, optIn, 0, option.length);

				cls = AbstractClassifier.forName(classifier, optIn);
				cls.buildClassifier(trainingData);
				
				Evaluation eval = new Evaluation(testData);
				eval.evaluateModel(cls, testData);

				// Show result
				System.out.println("  MCC on test data: " + mcc(eval));
				System.out.println("               AUC: " + eval.areaUnderROC(0));
				System.out.println("              Acc.: " + eval.pctCorrect());

			} catch (Exception e) {
				System.out.println("Configuration failed");
				e.printStackTrace();
			}
		}
	}
}