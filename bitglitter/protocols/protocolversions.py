import bitglitter.protocols.protocol_one.write.protocol_one_preprocess as protocol_one_preprocess
import bitglitter.protocols.protocol_one.write.protocol_one_renderlogic as protocol_one_renderlogic
import bitglitter.protocols.protocol_one.write.protocol_one_verifywriteparameters as protocol_one_verifywriteparameters
from bitglitter.protocols.protocolobjects import Protocol

#This is where protocol objects get instantiated from the various components it comprises of.
protocolOne = Protocol('1',
                       protocol_one_renderlogic.EncodeFrame,
                       "decoder",
                       verify_write_params_function=protocol_one_verifywriteparameters.verify_write_parameters,
                       pre_processing=protocol_one_preprocess.PreProcessor,
                       initializer_used="initializerProtocolOne"
                       )