"""Triangle probability distribution."""
import numpy
from scipy import special, misc

from ..baseclass import SimpleDistribution, LowerUpperDistribution
from .beta import beta_


class triangle(SimpleDistribution):
    """Triangle probability distribution."""

    def __init__(self, a=.5):
        # assert numpy.all(a>=0) and numpy.all(a<=1)
        super(triangle, self).__init__(dict(a=a))

    def _pdf(self, xloc, a):
        return numpy.where(xloc < a, 2*xloc/a, 2*(1-xloc)/(1-a))

    def _cdf(self, xloc, a):
        return numpy.where(xloc < a, xloc**2/(a+(a == 0)),
                (2*xloc-xloc*xloc-a)/(1-a+(a == 1)))

    def _ppf(self, qloc, a):
        return numpy.where(qloc<a, numpy.sqrt(qloc*a), 1-numpy.sqrt(1-a-qloc*(1-a)))

    def _mom(self, k, a):
        a_ = a*(a!=1)
        out = 2*(1.-a_**(k+1))/((k+1)*(k+2)*(1-a_))
        return numpy.where(a==1, 2./(k+2), out)

    def _lower(self, a):
        return 0.

    def _upper(self, a):
        return 1.

    def _ttr(self, k, a):
        if a == 0:
            return beta_()._ttr(k, 1, 2)
        if a == 1:
            return beta_()._ttr(k, 2, 1)

        from ...quadrature import quad_fejer, discretized_stieltjes
        q1, w1 = quad_fejer(int(1000*a), (0, a))
        q2, w2 = quad_fejer(int(1000*(1-a)), (a, 1))
        qloc = numpy.concatenate([q1,q2], 1)
        w = numpy.concatenate([w1,w2])*self._pdf(qloc[0], a)

        coeffs, _, _ = discretized_stieltjes(k, qloc, w)
        return coeffs[:, 0, -1]


class Triangle(LowerUpperDistribution):
    """
    Triangle Distribution.

    Must have lower <= midpoint <= upper.

    Args:
        lower (float, Distribution):
            Lower bound
        midpoint (float, Distribution):
            Location of the top
        upper (float, Distribution):
            Upper bound

    Examples:
        >>> distribution = chaospy.Triangle(-1, 0 ,1)
        >>> distribution
        Triangle(-1, 0.5, 1)
        >>> uloc = numpy.linspace(0, 1, 6)
        >>> uloc
        array([0. , 0.2, 0.4, 0.6, 0.8, 1. ])
        >>> xloc = distribution.inv(uloc)
        >>> xloc.round(3)
        array([-1.   , -0.368, -0.106,  0.106,  0.368,  1.   ])
        >>> numpy.allclose(distribution.fwd(xloc), uloc)
        True
        >>> distribution.pdf(xloc).round(3)
        array([0.   , 0.632, 0.894, 0.894, 0.632, 0.   ])
        >>> distribution.sample(4).round(3)
        array([ 0.168, -0.52 ,  0.685, -0.018])
        >>> distribution.mom(1).round(4)
        0.0
        >>> distribution.ttr([0, 1, 2, 3]).round(4)
        array([[-0.    ,  0.    , -0.    ,  0.    ],
               [ 4.    ,  0.1667,  0.2333,  0.2327]])

    """

    def __init__(self, lower=-1, midpoint=0, upper=1):
        midpoint = (midpoint-lower)*1./(upper-lower)
        super(Triangle, self).__init__(
            dist=triangle(midpoint),
            lower=lower,
            upper=upper,
            repr_args=["midpoint=%s" % midpoint],
        )
        self._repr_args = [lower, midpoint, upper]
