""" Train a LambdaMart (LTR) Method
"""
from __future__ import division
import pyltr
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
import cPickle as pickle
from wsd import *

#Columns = [entity_id, qid, score0, score1, score5, label]
outdir = os.path.join(baseresdir, 'wikify')
tr_file_name = os.path.join(home,'backup/datasets/ner/trainrepository.15000.30000.tsv')
data=pd.read_table(tr_file_name, header=None)

# Can't shuffle straighforwardly, I should group by quid, the shuffle
# But I guess shuffling is done in the estimator
#data = data.sample(frac=1)


num_cols = len(data.columns)

grouped=data.groupby(1)
total_len=len(grouped)
group = grouped.filter(lambda x:x.iloc[0,1] >= 0 and x.iloc[0,1] < 0.6*total_len)

#Train Data
#The following line does does the int-->float conversion, is it reliable? 
#Should I care later, while testing?
X_train = group.iloc[:,2:num_cols-1].as_matrix()

# Train the transformer and preprocess X_train
ltr_preprocessor = MinMaxScaler()
X_train=ltr_preprocessor.fit_transform(X_train)
ltr_preprocessor_fn = os.path.join(home,'backup/datasets/ner/ltr_preprocessor.pkl')
pickle.dump(ltr_preprocessor, open(ltr_preprocessor_fn, 'wb'))
####

y_train = group.iloc[:,num_cols-1].as_matrix()
qid_train = group.iloc[:,1].as_matrix()


#Validation Data
group=grouped.filter(lambda x:x.iloc[0,1] >= 0.6*total_len and x.iloc[0,1] < 0.8*total_len)
X_validate = group.iloc[:,2:num_cols-1].as_matrix()
X_validate = ltr_preprocessor.transform(X_validate)

y_validate = group.iloc[:,num_cols-1].as_matrix()
qid_validate = group.iloc[:,1].as_matrix()

#Test Data
group=grouped.filter(lambda x:x.iloc[0,1] >= 0.8*total_len and x.iloc[0,1] < 1.0*total_len)
X_test = group.iloc[:,2:num_cols-1].as_matrix()
X_test = ltr_preprocessor.transform(X_test)

y_test = group.iloc[:,num_cols-1].as_matrix()
qid_test = group.iloc[:,1].as_matrix()

monitor = pyltr.models.monitors.ValidationMonitor(
     X_validate, y_validate, qid_validate, metric=pyltr.metrics.NDCG(k=10), stop_after=250)
model = pyltr.models.LambdaMART(n_estimators=300, learning_rate=0.1, verbose = 1)
#lmart.fit(TX, TY, Tqid, monitor=monitor)
model.fit(X_train, y_train, qid_train, monitor=monitor)

metric = pyltr.metrics.NDCG(k=10)
Ts_pred = model.predict(X_test)
print 'Random ranking:', metric.calc_mean_random(qid_test, y_test)
print 'Our model:', metric.calc_mean(qid_test, y_test, Ts_pred)

model_file_name = os.path.join(home,'backup/datasets/ner/ltr.pkl')
pickle.dump(model, open(model_file_name, 'wb'))

print 'Model saved'