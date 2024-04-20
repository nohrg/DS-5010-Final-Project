import unittest
import numpy as np
import scipy.stats as stats

def calculate_cramers_v(contingency_table):
    '''
    Function-- calculate_cramers_v
        Calculate Cramer's V statistic for 2x2 contingency table
        containing enrollment #'s between programs A and B.

    Parameters:
        contingency_table (np.array) : 2 x 2 contingency table,
            containing Person ID enrollments and overlaps
            between Program A and B, formatted as follows:
            _ _ _ _ _ _ _ _ _ _
            | A & B  | A only  |
            |- - - - - - - - - |
            | B only | Neither |
            | - - - - - - - - -|
        
    Returns:
        cramers_v (float) : Cramer's V coefficient, rounded to 4 decimals
    '''
    # use scipy.stat's chi-squared contingency function
    # Note: even though we only need the chi2 statistic to calculate Cramer's V
    # all return values shown below by tuple assignment (for reader)
    chi2, pvalue, dof, expected_freq = stats.chi2_contingency(
        contingency_table, correction=False
        )
    
    # Total sample size
    n = np.sum(contingency_table)  
    
    # phi-squared = chi-squared / sample size
    phi2 = chi2 / n
    
    # Number of rows (r) and columns (k)
    r, k = contingency_table.shape
    
    cramers_v = np.sqrt(phi2 / min(k-1, r-1))
    return cramers_v.round(4)


class TestFunctions(unittest.TestCase):
    '''
    Most of our plot functions are hard to test via unittest
    as they produce visuals with Plotly/Dash.

    Likewise, we unittested our pandas functions by double checking
    by executing equivalent filtering steps in Google Sheets
    and checking against randomly selected rows of the filtered df
    (or doing count checks in spreadsheet vs. pd.shape or pd.size)

    Example #1:
    cont_table = create_contingency_table(program_dict, 
    'Girls Varsity Crew', 'Boys Varsity Football')

        expected:
        array([ [0,  178] , [226, 1551] ])

    The one case, however, that felt appropriate and necessary
    to test via unittest was our calculate_cramers_v function.
    Given that Cramer's V is a complicated but well-documented test,
    and that it was the one function that we relied on the most
    outside sources to implement, we felt like it was essential to
    ensure that it produced the expected results on various contingency tables.
    '''

    def test_cramers_v(self):
        # testing calculate_cramers_v with known 2x2 contingency table
        # and expected cramers_v coefficient

        data = np.array([[7,12], [9,8]])
        cramers_v = calculate_cramers_v(data)
        expected = 0.1617
        self.assertEqual(cramers_v, expected)

        # even though our package only sends 2x2 contingency tables
        # into calculate_cramers_v(), 
        # our code should still work for 2x3 table as well!
        data2 = np.array([[6,9], [8, 5], [12, 9]])
        cramers_v2 = calculate_cramers_v(data2)
        expected2 = 0.1775
        self.assertEqual(cramers_v2, expected2)

def main():
    unittest.main(verbosity=3)

if __name__ == "__main__":
    main()