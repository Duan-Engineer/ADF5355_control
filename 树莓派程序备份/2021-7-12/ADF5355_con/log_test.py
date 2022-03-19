import XAOLogHandlers as log
#a=log.getLogger(name="test1")
#a[1].error("this is a test!")

import ADF5355
a=ADF5355.register13()
a.set_register0(autocal=1,perscal=0,INT=1000)
a.set_register1(FRAC1=100)
a.set_register2(FRAC2=1000,MOD2=16383)
a.set_register3(SD1=1,PHR1=1,PHA1=1)
a.set_register4