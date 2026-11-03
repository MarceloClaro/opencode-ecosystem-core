"""Worker R928 standalone: imports pesados só no subprocesso isolado, sem rede."""
from __future__ import annotations

import argparse
import dataclasses
import enum
import json
from pathlib import Path
import sys


def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,
        default=lambda x:x.value if isinstance(x,enum.Enum) else dataclasses.asdict(x)),encoding='utf-8')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=('probe','demo'))
    parser.add_argument('--directory',type=Path,required=True)
    args=parser.parse_args(argv)
    if sys.version_info[:2]!=(3,12): raise RuntimeError('Python 3.12 required')
    sys.path.insert(0,'/source')
    import numpy as np
    import tensorflow as tf
    from ai_edge_litert import interpreter as lite
    from ai_edge_quantizer import quantizer,recipe
    if not str(Path(quantizer.__file__)).startswith('/source/'):
        raise RuntimeError('Quantizer is not the pinned source mount')
    tf.config.set_visible_devices([], 'GPU')
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
    from importlib import metadata
    versions={name:metadata.version(name) for name in ('tf-nightly','ai-edge-litert-nightly','numpy','immutabledict','backports.strenum')}
    if args.operation=='probe':
        result={'status':'imports_verified_cpu','python':sys.version.split()[0],
                'versions':versions,'source_import':'/source','model_created':False}
    else:
        work=args.directory
        weights=np.linspace(-0.75,0.75,32*64,dtype=np.float32).reshape(32,64)
        bias=np.linspace(-0.1,0.1,64,dtype=np.float32)
        class Tiny(tf.Module):
            @tf.function(input_signature=[tf.TensorSpec([1,32],tf.float32,name='x')],autograph=False)
            def serve(self,x):
                return {'y':tf.nn.relu(tf.matmul(x,tf.constant(weights))+tf.constant(bias))}
        model=Tiny()
        concrete=model.serve.get_concrete_function()
        converter=tf.lite.TFLiteConverter.from_concrete_functions([concrete],model)
        converter.optimizations=[]
        float_model=converter.convert()
        (work/'float.tflite').write_bytes(float_model)
        qt=quantizer.Quantizer(str(work/'float.tflite'))
        qt.load_quantization_recipe(recipe.dynamic_wi8_afp32())
        if qt.need_calibration: raise RuntimeError('Dynamic recipe unexpectedly requires calibration')
        quantized=qt.quantize()
        quantized.export_model(str(work/'quantized.tflite'))
        write_json(work/'recipe.json',qt.get_quantization_recipe())
        rng=np.random.default_rng(42)
        inputs=rng.uniform(-1.0,1.0,(16,1,32)).astype(np.float32)
        reference=np.maximum(inputs.reshape(16,32)@weights+bias,0).astype(np.float64)
        def evaluate(path):
            interpreter=lite.Interpreter(model_path=str(path),num_threads=1,
                experimental_op_resolver_type=lite.OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES)
            interpreter.allocate_tensors()
            input_detail=interpreter.get_input_details()[0]
            output_detail=interpreter.get_output_details()[0]
            if input_detail['dtype']!=np.float32 or output_detail['dtype']!=np.float32:
                raise RuntimeError('Unexpected synthetic model IO dtype')
            results=[]
            for sample in inputs:
                interpreter.set_tensor(input_detail['index'],sample)
                interpreter.invoke()
                results.append(interpreter.get_tensor(output_detail['index']).reshape(-1).astype(np.float64))
            return np.asarray(results),sum(d['dtype']==np.int8 for d in interpreter.get_tensor_details())
        fp,_=evaluate(work/'float.tflite')
        q,count=evaluate(work/'quantized.tflite')
        metrics={'conversion_max_abs':float(np.max(np.abs(fp-reference))),
                 'quantized_mse':float(np.mean(np.square(fp-q))),
                 'quantized_max_abs':float(np.max(np.abs(fp-q))),
                 'int8_tensor_count':int(count),'float_bytes':len(float_model),
                 'quantized_bytes':(work/'quantized.tflite').stat().st_size,'samples':16}
        metrics['size_ratio']=metrics['quantized_bytes']/metrics['float_bytes']
        write_json(work/'evaluation.json',{'float':fp.tolist(),'quantized':q.tolist(),'reference':reference.tolist()})
        write_json(work/'metrics.json',metrics)
        result={'status':'synthetic_worker_completed','metrics':metrics,'versions':versions,
            'training_executed':False,'external_checkpoint_downloaded':False,
            'synthetic_inference_executed':True,'quality_scope':'synthetic_numeric_only'}
    print('EDGE_QUANTIZER_RESULT='+json.dumps(result,sort_keys=True,allow_nan=False))
    return 0


if __name__=='__main__': raise SystemExit(main())
