def plotROCCurve(y_test, prediction_prob):
    fpr, tpr, thresholds = roc_curve(y_test, prediction_prob[:,1])
    roc_auc = auc(fpr, tpr)
    plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
    plot([0, 1], [0, 1], 'k--')
    xlabel('False Positive Rate')
    ylabel('True Positive Rate')
    plt.legend(bbox_to_anchor=(0.9, 0.2),
               bbox_transform=plt.gcf().transFigure)
    savefig('logistic_regression_aucroc.png', bbox_inches='tight', dpi=150)