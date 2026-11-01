import unittest
from app import load_data, rank

class PlannerTests(unittest.TestCase):
    def setUp(self): self.data=load_data()
    def test_different_destinations(self):
        r=rank('Campus location A','Campus location B','12:00',self.data)['results']
        self.assertEqual([(x['name'],x['total']) for x in r],[('Restaurant B',23),('Restaurant A',35),('Restaurant C',37)])
    def test_arrival_band_boundary(self):
        r=rank('Campus location A','Campus location B','11:56',self.data)['results']
        self.assertEqual(next(x for x in r if x['name']=='Restaurant A')['wait'],22)
    def test_same_location(self):
        r=rank('Campus location A','Campus location A','10:00',self.data)['results']
        self.assertEqual(r[0]['total'],13)
    def test_outside_coverage(self):
        self.assertFalse(rank('Campus location A','Campus location B','19:00',self.data)['results'])
    def test_missing_and_ties(self):
        routes,locations,restaurants,bands=self.data
        routes=routes.copy();routes.pop(frozenset(('Campus location A','Restaurant A')))
        r=rank('Campus location A','Campus location B','12:00',(routes,locations,restaurants,bands))
        self.assertEqual(len(r['unavailable']),1)
        sample=({frozenset(('X','R')):2,frozenset(('X','S')):2},['X'],{'R':[0],'S':[0]},[(0,1440,'all')])
        self.assertEqual([x['rank'] for x in rank('X','X','12:00',sample)['results']],[1,1])
    def test_invalid_time(self):
        with self.assertRaises(ValueError):rank('Campus location A','Campus location B','25:00',self.data)

if __name__=='__main__':unittest.main()
