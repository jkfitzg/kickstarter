import numpy as np
import pandas as pd

def make_success_fail_df(predictor_df):
	n_rows = np.shape(predictor_df)[0]
	outcomes_df = pd.DataFrame(0, index = np.arange(n_rows), columns = ['Outcome'])

	successful_campaigns_i = np.where(predictor_df['Pledged']>=predictor_df['Goal'])[0]
	outcomes_df.ix[successful_campaigns_i,'Outcome'] = 1
	return outcomes_df

def make_ships_intn_df(predictor_df):
	# returns a pd with 0/1 international shipping, where US only and unconfirmed 
	# are coded as 0

	# zero by default
	n_rows = np.shape(predictor_df)[0]
	new_ships_intn_df = pd.DataFrame(0, index = np.arange(n_rows), columns = ['Ships_intn'])

	confirmed_intn_ship_i = np.where(predictor_df['Ships_intn'] == 1)[0]
	new_ships_intn_df.ix[confirmed_intn_ship_i,'Ships_intn'] = 1

	return new_ships_intn_df

def make_categorical_df_from_str(predictor_df):
	# only send in columns of interest

	from sklearn import preprocessing
	lb = preprocessing.LabelBinarizer()
	binary_array = lb.fit_transform(predictor_df)

	categorical_df = pd.DataFrame(binary_array,columns=np.unique(predictor_df))
	return categorical_df

def make_categorical_df_from_num(predictor_df,col_names=None):
	from sklearn.preprocessing import OneHotEncoder
	enc = OneHotEncoder()

	categorical_array = enc.fit_transform(predictor_df).toarray()
	categorical_df = pd.DataFrame(categorical_array,columns=col_names)
	return categorical_df