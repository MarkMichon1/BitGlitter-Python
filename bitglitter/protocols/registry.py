import bitglitter.write.preprocessors as protocol_one_preprocess
import bitglitter.write.renderlogic as protocol_one_renderlogic
import bitglitter.write.writeparameterverify as protocol_one_verifywriteparameters
from bitglitter.protocols.protocol import Protocol

#This is where protocol objects get instantiated from the various components it comprises of.
protocol_one = Protocol('1',
                        protocol_one_renderlogic.EncodeFrame,
                       "decoder",
                        verify_write_params_function=protocol_one_verifywriteparameters.verify_write_parameters,
                        pre_processing=protocol_one_preprocess.PreProcessor,
                        initializer_used="initializerProtocolOne"
                        )